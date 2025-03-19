import os
import time
import aiofiles
import uvicorn
from fastapi import Request
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, Response
from fastapi import HTTPException
import mimetypes
from urllib.parse import unquote

from byzerllm.log import init_logger
from byzerllm.utils import random_uuid
from byzerllm.version import __version__ as version
from byzerllm.utils.client import ByzerLLM, LLMRequest
from byzerllm.utils.client.entrypoints.openai.serving_chat import OpenAIServingChat
from byzerllm.utils.client.entrypoints.openai.serving_completion import OpenAIServingCompletion
from byzerllm.utils.client.entrypoints.openai.protocol import (
    ModelList,
    ModelCard,
    ModelPermission,
    ChatCompletionRequest,
    ErrorResponse,
    CompletionRequest,
    EmbeddingCompletionRequest,
    EmbeddingResponse,
    EmbeddingResponseData,
    UsageInfo,
)
from pydantic import BaseModel
from typing import List,Optional

# If support dotenv, use it
if os.path.exists(".env"):
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

logger = init_logger(__name__)

llm_client: ByzerLLM = None
openai_serving_chat: OpenAIServingChat = None
openai_serving_completion: OpenAIServingCompletion = None

TIMEOUT_KEEP_ALIVE = 5  # seconds
# timeout in 10 minutes. Streaming can take longer than 3 min
TIMEOUT = float(os.environ.get("BYZERLLM_APISERVER_HTTP_TIMEOUT", 600))

router_app = FastAPI()


@router_app.get("/health")
async def health() -> Response:
    """Health check."""
    return Response(status_code=200)


@router_app.get("/v1/models")
async def show_available_models():
    models = await openai_serving_chat.show_available_models()
    return JSONResponse(content=models.model_dump())


@router_app.get("/version")
async def show_version():
    return JSONResponse(content={"version": version})


@router_app.get("/v1/models", response_model=ModelList)
async def models() -> ModelList:
    """Show available models. Right now we only have one model."""
    model_cards = [
        ModelCard(
            id="",
            root="",
            permission=[ModelPermission()]
        )
    ]
    return ModelList(data=model_cards)


@router_app.post("/v1/completions")
async def create_completion(
        body: CompletionRequest,
        request: Request
):
    generator = await openai_serving_completion.create_completion(body, request)
    if isinstance(generator, ErrorResponse):
        return JSONResponse(
            content=generator.model_dump(),
            status_code=generator.code
        )
    if body.stream:
        return StreamingResponse(
            content=generator,
            media_type="text/event-stream"
        )
    else:
        return JSONResponse(content=generator.model_dump())


@router_app.post("/v1/chat/completions")
async def create_chat_completion(
        body: ChatCompletionRequest,
        request: Request,
):
    """Completion API similar to OpenAI's API.

    See  https://platform.openai.com/docs/api-reference/chat/create
    for the API specification. This API mimics the OpenAI ChatCompletion API.

    NOTE: Currently we do not support the following features:
        - function_call (Users should implement this by themselves)
        - logit_bias (to be supported by vLLM engine)
    """    
    generator = await openai_serving_chat.create_chat_completion(body, request)
    if isinstance(generator, ErrorResponse):
        return JSONResponse(
            content=generator.model_dump(),
            status_code=generator.code
        )
    if body.stream:
        return StreamingResponse(
            content=generator,
            media_type="text/event-stream"
        )
    else:
        return JSONResponse(content=generator.model_dump())


@router_app.post("/v1/embeddings")
async def embed(body: EmbeddingCompletionRequest):
    """Generate embeddings for given input text.
    
    Args:
        body: The embedding request containing input text and parameters.
        
    Returns:
        EmbeddingResponse with embeddings and usage statistics.
    """
    embedding_id = f"embed-{random_uuid()}"
    
    # Handle both string and list inputs
    inputs = body.input if isinstance(body.input, list) else [body.input]
    
    # Generate embeddings for each input
    results_list = []
    for text in inputs:
        result = llm_client.emb(body.model, request=LLMRequest(instruction=text))
        results_list.extend(result)

    # Build response data
    data = [
        EmbeddingResponseData(
            embedding=result.output,
            index=i,
            object="embedding"
        )
        for i, result in enumerate(results_list)
    ]
    
    # Calculate token usage (simplified)
    token_count = sum(len(str(input).split()) for input in inputs)
    
    return EmbeddingResponse(
        data=data,
        model=body.model,
        object="list",
        usage=UsageInfo(
            prompt_tokens=token_count,
            total_tokens=token_count
        ),
        created=int(time.time()),
        id=embedding_id
    )

@router_app.get("/static/{full_path:path}")
async def serve_image(full_path: str, request: Request):
    
    allowed_file_type = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    
    if any(full_path.endswith(ext) for ext in allowed_file_type):
        try:
            # 获取文件的完整路径，并进行URL解码
            file_path = unquote(full_path)
            # 使用 os.path.normpath 来标准化路径，自动处理不同操作系统的路径分隔符
            file_path = os.path.normpath(file_path)
            if not os.path.isabs(file_path):
                file_path = os.path.join("/", file_path)
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
                
            # 异步读取文件内容
            async with aiofiles.open(file_path, "rb") as f:
                content = await f.read()
            
            # 获取文件的 MIME 类型
            content_type = mimetypes.guess_type(file_path)[0]
            if not content_type:
                content_type = "application/octet-stream"
                
            # 返回文件内容
            return Response(content=content, media_type=content_type)
        except FileNotFoundError as e:
            logger.error(f"Image not found: {str(e)}")
            raise HTTPException(status_code=404, detail=f"Image not found: {str(e)}")
        except PermissionError as e:
            logger.error(f"Permission denied: {str(e)}")
            raise HTTPException(status_code=403, detail=f"Permission denied: {str(e)}")
        except Exception as e:
            logger.error(f"Error serving image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error serving image: {str(e)}")
    
    # 如果路径中没有图片, 返回 404
    raise HTTPException(status_code=404, detail="Only images are supported")

class ServerArgs(BaseModel):
    host: str = None
    port: int = 8000
    workers: int = 4
    uvicorn_log_level: str = "info"
    allow_credentials: bool = False
    allowed_origins: List[str] = ["*"]  
    allowed_methods: List[str] = ["*"]
    allowed_headers: List[str] = ["*"]
    api_key: str = None
    served_model_name: str = None
    prompt_template: str = None
    response_role: str = "assistant"
    ssl_keyfile: str = None
    ssl_certfile: str = None 
    doc_dir: str = "" 
    tokenizer_path: Optional[str] = None     

def serve(llm:ByzerLLM, args: ServerArgs):
    
    logger.info(f"ByzerLLM API server version {version}")
    logger.info(f"args: {args}")

    router_app.add_middleware(
        CORSMiddleware,
        allow_origins=args.allowed_origins,
        allow_credentials=args.allow_credentials,
        allow_methods=args.allowed_methods,
        allow_headers=args.allowed_headers,
    )
    
    if token := os.environ.get("BYZERLLM_API_KEY") or args.api_key:

        @router_app.middleware("http")
        async def authentication(request: Request, call_next):
            if not request.url.path.startswith("/v1"):
                return await call_next(request)
            if request.headers.get("Authorization") != "Bearer " + token:
                return JSONResponse(
                    content={"error": "Unauthorized"},
                    status_code=401
                )
            return await call_next(request)

    # Register labels for metrics
    # add_global_metrics_labels(model_name=engine_args.model)
    global llm_client
    llm_client = llm
    
    global openai_serving_chat
    openai_serving_chat = OpenAIServingChat(
        llm_client=llm_client,
        response_role=args.response_role,
        server_model_name=args.served_model_name,
        prompt_template=args.prompt_template
    )
    global openai_serving_completion
    openai_serving_completion = OpenAIServingCompletion(
        llm_client=llm_client,
        server_model_name=args.served_model_name,
        prompt_template=args.prompt_template
    )

    # 如果使用workers>1或reload=True，必须使用导入字符串而不是应用实例    
    uvicorn.run(
        router_app,
        host=args.host,
        port=args.port,
        log_level=args.uvicorn_log_level,
        timeout_keep_alive=TIMEOUT_KEEP_ALIVE,
        ssl_keyfile=args.ssl_keyfile,
        ssl_certfile=args.ssl_certfile
    )
