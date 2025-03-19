"""
活动上下文管理器 - 子系统的主要接口
"""

import os
import sys
import time
import threading
import queue
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple, Set
from loguru import logger as global_logger
import byzerllm
import re
from pydantic import BaseModel, Field

from autocoder.common import AutoCoderArgs
from autocoder.common.action_yml_file_manager import ActionYmlFileManager
from autocoder.common.printer import Printer
from autocoder.memory.directory_mapper import DirectoryMapper
from autocoder.memory.active_package import ActivePackage
from autocoder.memory.async_processor import AsyncProcessor


class ActiveFileSections(BaseModel):
    """活动文件内容的各个部分"""
    header: str = Field(default="", description="文件标题部分")
    current_change: str = Field(default="", description="当前变更部分")
    document: str = Field(default="", description="文档部分")


class ActiveFileContext(BaseModel):
    """单个活动文件的上下文信息"""
    directory_path: str = Field(..., description="目录路径")
    active_md_path: str = Field(..., description="活动文件路径")
    content: str = Field(..., description="文件完整内容")
    sections: ActiveFileSections = Field(..., description="文件内容各部分")
    files: List[str] = Field(default_factory=list, description="与该活动文件相关的源文件列表")


class FileContextsResult(BaseModel):
    """文件上下文查询结果"""
    contexts: Dict[str, ActiveFileContext] = Field(
        default_factory=dict, 
        description="键为目录路径，值为活动文件上下文"
    )
    not_found_files: List[str] = Field(
        default_factory=list,
        description="未找到对应活动上下文的文件列表"
    )


class ActiveContextManager:
    """
    ActiveContextManager是活动上下文跟踪子系统的主要接口。
    
    该类负责：
    1. 从YAML文件加载任务数据
    2. 映射目录结构
    3. 生成活动上下文文档
    4. 管理异步任务执行
    
    该类实现了单例模式，确保系统中只有一个实例。
    """
    
    # 类变量，用于存储单例实例
    _instance = None
    _is_initialized = False
    
    # 任务队列和队列处理线程
    _task_queue = None
    _queue_thread = None
    _queue_lock = None
    _is_processing = False
    
    def __new__(cls, llm: byzerllm.ByzerLLM = None, args: AutoCoderArgs = None):
        """
        实现单例模式，确保只创建一个实例
        
        Args:
            llm: ByzerLLM实例，用于生成文档内容
            args: AutoCoderArgs实例，包含配置信息
        
        Returns:
            ActiveContextManager: 单例实例
        """
        if cls._instance is None:
            cls._instance = super(ActiveContextManager, cls).__new__(cls)
            cls._instance._is_initialized = False
        return cls._instance
    
    def __init__(self, llm: byzerllm.ByzerLLM,source_dir:str):
        """
        初始化活动上下文管理器
        
        Args:
            llm: ByzerLLM实例，用于生成文档内容            
        """
        # 如果已经初始化过，则直接返回
        if self._is_initialized:
            return
        self.source_dir = source_dir
        # 设置日志目录和文件
        log_dir = os.path.join(source_dir, ".auto-coder", "active-context")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "active.log")
        
        # 配置全局日志输出到文件，不输出到控制台
        global_logger.configure(
            handlers=[
                # 移除控制台输出，只保留文件输出
                {"sink": log_file, "level": "DEBUG", "rotation": "10 MB", "retention": "1 week", 
                 "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}"}
            ]
        )
        
        # 创建专用的logger实例
        self.logger = global_logger.bind(name="ActiveContextManager")
        self.logger.info(f"初始化 ActiveContextManager，日志输出到 {log_file}")
            
        self.llm = llm        
        self.directory_mapper = DirectoryMapper()
        self.active_package = ActivePackage(llm)
        self.async_processor = AsyncProcessor()
        self.yml_manager = ActionYmlFileManager(source_dir)
        self.tasks = {}  # 用于跟踪任务状态
        self.printer = Printer()
        
        # 初始化任务队列和锁
        self.__class__._task_queue = queue.Queue()
        self.__class__._queue_lock = threading.Lock()
        
        # 启动队列处理线程
        self.__class__._queue_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.__class__._queue_thread.start()
        
        # 标记为已初始化
        self._is_initialized = True                    
    
    def _process_queue(self):
        """
        处理任务队列的后台线程
        确保一次只有一个任务在运行
        """
        while True:
            try:
                # 从队列中获取任务
                task = self._task_queue.get()
                if task is None:
                    # None 是退出信号
                    break
                    
                # 设置处理标志
                with self._queue_lock:
                    self.__class__._is_processing = True
                    
                # 解包任务参数
                task_id, query, changed_urls, current_urls = task
                
                # 更新任务状态为运行中
                self.tasks[task_id]['status'] = 'running'                
                                
                self._process_changes_async(task_id, query, changed_urls, current_urls)                
                
                # 重置处理标志
                with self._queue_lock:
                    self.__class__._is_processing = False
                    
                # 标记任务完成
                self._task_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Error in queue processing thread: {e}")
                # 重置处理标志，确保队列可以继续处理
                with self._queue_lock:
                    self.__class__._is_processing = False
    
    def process_changes(self, args:AutoCoderArgs) -> str:
        """
        处理代码变更，创建活动上下文（非阻塞）
        
        Args:
            args: AutoCoderArgs实例，包含配置信息
        
        Returns:
            str: 任务ID，可用于后续查询任务状态
        """
        try:
            # 使用参数中的文件或者指定的文件
            if not args.file:
                raise ValueError("action file is required")            
            
            file_name = os.path.basename(args.file)
            # 从YAML文件加载数据
            yaml_content = self.yml_manager.load_yaml_content(file_name)
            
            # 提取需要的信息
            query = yaml_content.get('query', '')
            changed_urls = yaml_content.get('add_updated_urls', [])
            current_urls = yaml_content.get('urls', []) + yaml_content.get('dynamic_urls', [])
            
            # 创建任务ID
            task_id = f"active_context_{int(time.time())}_{file_name}"
            
            # 更新任务状态
            self.tasks[task_id] = {
                'status': 'queued',
                'start_time': datetime.now(),
                'file_name': file_name,
                'query': query,
                'changed_urls': changed_urls,
                'current_urls': current_urls,
                'queue_position': self._task_queue.qsize() + (1 if self._is_processing else 0)
            }
            
            # 直接启动后台线程处理任务，不通过队列
            thread = threading.Thread(
                target=self._execute_task_in_background,
                args=(task_id, query, changed_urls, current_urls),
                daemon=True  # 使用守护线程，主程序退出时自动结束
            )
            thread.start()
            
            # 记录任务已启动，并立即返回
            self.logger.info(f"Task {task_id} started in background thread")
            return task_id
            
        except Exception as e:
            self.logger.error(f"Error in process_changes: {e}")            
            raise
    
    def _execute_task_in_background(self, task_id: str, query: str, changed_urls: List[str], current_urls: List[str]):
        """
        在后台线程中执行任务，处理所有日志重定向
        
        Args:
            task_id: 任务ID
            query: 用户查询
            changed_urls: 变更的文件列表
            current_urls: 当前相关的文件列表
        """
        try:
            # 更新任务状态为运行中
            self.tasks[task_id]['status'] = 'running'
            
            # 重定向输出并执行任务
            self._process_changes_async(task_id, query, changed_urls, current_urls)
            
            # 更新任务状态为已完成
            self.tasks[task_id]['status'] = 'completed'
            self.tasks[task_id]['completion_time'] = datetime.now()
            
        except Exception as e:
            # 记录错误，但不允许异常传播到主线程
            error_msg = f"Background task {task_id} failed: {str(e)}"
            self.logger.error(error_msg)
            self.tasks[task_id]['status'] = 'failed'
            self.tasks[task_id]['error'] = error_msg
    
    def _process_changes_async(self, task_id: str, query: str, changed_urls: List[str], current_urls: List[str]):
        """
        实际处理变更的异步方法
        
        Args:
            task_id: 任务ID
            query: 用户查询/需求
            changed_urls: 变更的文件路径列表
            current_urls: 当前相关的文件路径列表
        """
        try:
            self.logger.info(f"==== 开始处理任务 {task_id} ====")
            self.logger.info(f"查询内容: {query}")
            self.logger.info(f"变更文件数量: {len(changed_urls)}")
            self.logger.info(f"相关文件数量: {len(current_urls)}")
            
            if changed_urls:
                self.logger.debug(f"变更文件列表: {', '.join(changed_urls[:5])}{'...' if len(changed_urls) > 5 else ''}")
            
            self.tasks[task_id]['status'] = 'running'
            
            # 获取当前任务的文件名
            file_name = self.tasks[task_id].get('file_name')
            self.logger.info(f"任务关联文件: {file_name}")
            
            # 获取文件变更信息
            file_changes = {}
            if file_name:
                self.logger.info(f"正在获取提交变更信息...")
                commit_changes = self.yml_manager.get_commit_changes(file_name)
                if commit_changes and len(commit_changes) > 0:
                    # commit_changes结构为 [(query, urls, changes)]
                    _, _, changes = commit_changes[0]
                    file_changes = changes
                    self.logger.info(f"成功获取到 {len(file_changes)} 个文件变更")
                else:
                    self.logger.warning("未找到提交变更信息")
            
            # 1. 映射目录
            self.logger.info("开始映射目录结构...")
            directory_contexts = self.directory_mapper.map_directories(
                self.source_dir, changed_urls, current_urls
            )
            self.logger.info(f"目录映射完成，找到 {len(directory_contexts)} 个相关目录")
            
            # 2. 处理每个目录
            processed_dirs = []
            for i, context in enumerate(directory_contexts):
                dir_path = context['directory_path']
                self.logger.info(f"[{i+1}/{len(directory_contexts)}] 开始处理目录: {dir_path}")
                try:
                    self._process_directory_context(context, query, file_changes)
                    processed_dirs.append(os.path.basename(dir_path))
                    self.logger.info(f"目录 {dir_path} 处理完成")
                except Exception as e:
                    self.logger.error(f"处理目录 {dir_path} 时出错: {str(e)}")
                
            # 3. 更新任务状态
            self.tasks[task_id]['status'] = 'completed'
            self.tasks[task_id]['completion_time'] = datetime.now()
            self.tasks[task_id]['processed_dirs'] = processed_dirs
            
            duration = (datetime.now() - self.tasks[task_id]['start_time']).total_seconds()
            self.logger.info(f"==== 任务 {task_id} 处理完成 ====")
            self.logger.info(f"总耗时: {duration:.2f}秒")
            self.logger.info(f"处理的目录数: {len(processed_dirs)}")
        
        except Exception as e:
            # 记录错误
            self.logger.error(f"任务 {task_id} 失败: {str(e)}", exc_info=True)
            self.tasks[task_id]['status'] = 'failed'
            self.tasks[task_id]['error'] = str(e)
    
    def _process_directory_context(self, context: Dict[str, Any], query: str, file_changes: Dict[str, Tuple[str, str]] = None):
        """
        处理单个目录上下文
        
        Args:
            context: 目录上下文字典
            query: 用户查询/需求
            file_changes: 文件变更字典，键为文件路径，值为(变更前内容, 变更后内容)的元组
        """
        try:
            directory_path = context['directory_path']
            self.logger.debug(f"--- 处理目录上下文开始: {directory_path} ---")
            
            # 1. 确保目录存在
            target_dir = self._get_active_context_path(directory_path)
            os.makedirs(target_dir, exist_ok=True)
            self.logger.debug(f"目标目录准备完成: {target_dir}")
            
            # 2. 检查是否有现有的active.md文件
            existing_file_path = os.path.join(target_dir, "active.md")
            if os.path.exists(existing_file_path):
                self.logger.info(f"找到现有 active.md 文件: {existing_file_path}")
                try:
                    with open(existing_file_path, 'r', encoding='utf-8') as f:
                        existing_content_preview = f.read(500)
                    self.logger.debug(f"现有文件内容预览: {existing_content_preview[:100]}...")
                except Exception as e:
                    self.logger.warning(f"无法读取现有文件内容: {str(e)}")
            else:
                existing_file_path = None
                self.logger.info(f"目录 {directory_path} 没有找到现有的 active.md 文件")
            
            # 记录目录中的文件信息
            changed_files = context.get('changed_files', [])
            current_files = context.get('current_files', [])
            self.logger.debug(f"目录中变更文件数: {len(changed_files)}")
            self.logger.debug(f"目录中当前文件数: {len(current_files)}")
            
            # 过滤出当前目录相关的文件变更
            directory_changes = {}
            if file_changes:
                self.logger.debug(f"开始筛选与目录相关的文件变更...")
                # 获取当前目录下的所有文件路径
                dir_files = []
                for file_info in changed_files:
                    file_path = file_info['path']
                    dir_files.append(file_path)
                    self.logger.debug(f"添加变更文件: {file_path}")
                
                for file_info in current_files:
                    file_path = file_info['path']
                    dir_files.append(file_path)
                    self.logger.debug(f"添加当前文件: {file_path}")
                
                # 从file_changes中获取当前目录文件的变更
                for file_path, change_info in file_changes.items():
                    if file_path in dir_files:
                        directory_changes[file_path] = change_info
                        old_content, new_content = change_info
                        old_preview = old_content[:50] if old_content else "(空)"
                        new_preview = new_content[:50] if new_content else "(空)"
                        self.logger.debug(f"文件变更: {file_path}")
                        self.logger.debug(f"  旧内容: {old_preview}...")
                        self.logger.debug(f"  新内容: {new_preview}...")
                
                self.logger.info(f"找到 {len(directory_changes)} 个与目录 {directory_path} 相关的文件变更")
            else:
                self.logger.debug("没有提供文件变更信息")
            
            # 3. 生成活动文件内容
            self.logger.info(f"开始为目录 {directory_path} 生成活动文件内容...")
            markdown_content = self.active_package.generate_active_file(
                context, 
                query,
                existing_file_path=existing_file_path,
                file_changes=directory_changes
            )
            
            content_length = len(markdown_content)
            self.logger.debug(f"生成的活动文件内容长度: {content_length} 字符")
            if content_length > 0:
                self.logger.debug(f"内容预览: {markdown_content[:200]}...")
            
            # 4. 写入文件
            active_md_path = os.path.join(target_dir, "active.md")
            self.logger.info(f"正在写入活动文件: {active_md_path}")
            with open(active_md_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
                
            self.logger.info(f"成功创建/更新目录 {directory_path} 的活动文件")
            self.logger.debug(f"--- 处理目录上下文完成: {directory_path} ---")
            
        except Exception as e:
            self.logger.error(f"处理目录 {context.get('directory_path', 'unknown')} 时出错: {str(e)}", exc_info=True)
            raise
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 任务状态信息
        """
        if task_id not in self.tasks:
            return {'status': 'not_found', 'task_id': task_id}
        
        task = self.tasks[task_id]
        
        # 计算任务运行时间
        start_time = task.get('start_time')
        if task.get('status') == 'completed':
            completion_time = task.get('completion_time')
            if start_time and completion_time:
                duration = (completion_time - start_time).total_seconds()
            else:
                duration = None
            elapsed = None
        else:
            if start_time:
                elapsed = (datetime.now() - start_time).total_seconds()
            else:
                elapsed = None
            duration = None
        
        # 构建日志文件路径
        log_file_path = None
        if 'file_name' in task:
            log_dir = os.path.join(self.source_dir, '.auto-coder', 'active-context', 'logs')
            log_file_path = os.path.join(log_dir, f'{task_id}.log')
            if not os.path.exists(log_file_path):
                log_file_path = None
        
        # 构建返回结果
        result = {
            'task_id': task_id,
            'status': task.get('status', 'unknown'),
            'file_name': task.get('file_name'),
            'start_time': start_time.strftime("%Y-%m-%d %H:%M:%S") if start_time else None,
        }
        
        # 添加可选信息
        if 'completion_time' in task:
            result['completion_time'] = task['completion_time'].strftime("%Y-%m-%d %H:%M:%S")
        
        if elapsed is not None:
            mins, secs = divmod(elapsed, 60)
            hrs, mins = divmod(mins, 60)
            result['elapsed'] = f"{int(hrs):02d}:{int(mins):02d}:{int(secs):02d}"
        
        if duration is not None:
            mins, secs = divmod(duration, 60)
            hrs, mins = divmod(mins, 60)
            result['duration'] = f"{int(hrs):02d}:{int(mins):02d}:{int(secs):02d}"
        
        if 'processed_dirs' in task:
            result['processed_dirs'] = task['processed_dirs']
            result['processed_dirs_count'] = len(task['processed_dirs'])
        
        if 'error' in task:
            result['error'] = task['error']
        
        if log_file_path and os.path.exists(log_file_path):
            result['log_file'] = log_file_path
            
            # 尝试获取日志文件大小
            try:
                file_size = os.path.getsize(log_file_path)
                result['log_file_size'] = f"{file_size / 1024:.2f} KB"
            except:
                pass
        
        return result
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        获取所有任务状态
        
        Returns:
            List[Dict]: 所有任务的状态信息
        """
        return [{'task_id': tid, **task} for tid, task in self.tasks.items()]
    
    def get_running_tasks(self) -> List[Dict[str, Any]]:
        """
        获取所有正在运行的任务
        
        Returns:
            List[Dict]: 所有正在运行的任务的状态信息
        """
        return [{'task_id': tid, **task} for tid, task in self.tasks.items() 
                if task['status'] in ['running', 'queued']]
    
    def load_active_contexts_for_files(self, file_paths: List[str]) -> FileContextsResult:
        """
        根据文件路径列表，找到并加载对应的活动上下文文件
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            FileContextsResult: 包含活动上下文信息的结构化结果
        """
        try:
            result = FileContextsResult()
            
            # 记录未找到对应活动上下文的文件
            found_files: Set[str] = set()
            
            # 1. 获取文件所在的唯一目录列表
            directories = set()
            for file_path in file_paths:
                # 获取文件所在的目录
                dir_path = os.path.dirname(file_path)
                if os.path.exists(dir_path):
                    directories.add(dir_path)
            
            # 2. 查找每个目录的活动上下文文件
            for dir_path in directories:
                # 获取活动上下文目录路径
                active_context_dir = self._get_active_context_path(dir_path)
                active_md_path = os.path.join(active_context_dir, "active.md")
                
                # 检查active.md文件是否存在
                if os.path.exists(active_md_path):
                    try:
                        # 读取文件内容
                        with open(active_md_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 解析文件内容
                        sections_dict = self._parse_active_md_content(content)
                        sections = ActiveFileSections(**sections_dict)
                        
                        # 找到相关的文件
                        related_files = [f for f in file_paths if dir_path in f]
                        
                        # 记录找到了对应活动上下文的文件
                        found_files.update(related_files)
                        
                        # 创建活动文件上下文
                        active_context = ActiveFileContext(
                            directory_path=dir_path,
                            active_md_path=active_md_path,
                            content=content,
                            sections=sections,
                            files=related_files
                        )
                        
                        # 添加到结果
                        result.contexts[dir_path] = active_context
                        
                        self.logger.info(f"已加载目录 {dir_path} 的活动上下文文件")
                    except Exception as e:
                        self.logger.error(f"读取活动上下文文件 {active_md_path} 时出错: {e}")
            
            # 3. 记录未找到对应活动上下文的文件
            result.not_found_files = [f for f in file_paths if f not in found_files]
            
            return result
            
        except Exception as e:
            self.logger.error(f"加载活动上下文失败: {e}")
            return FileContextsResult(not_found_files=file_paths)
    
    def _parse_active_md_content(self, content: str) -> Dict[str, str]:
        """
        解析活动上下文文件内容，提取各个部分
        
        Args:
            content: 活动上下文文件内容
            
        Returns:
            Dict[str, str]: 包含标题、当前变更和文档部分的字典
        """
        try:
            result = {
                'header': '',
                'current_change': '',
                'document': ''
            }
            
            # 提取标题部分（到第一个二级标题之前）
            header_match = re.search(r'^(.*?)(?=\n## )', content, re.DOTALL)
            if header_match:
                result['header'] = header_match.group(1).strip()
            
            # 提取当前变更部分
            current_change_match = re.search(r'## 当前变更\s*\n(.*?)(?=\n## |$)', content, re.DOTALL)
            if current_change_match:
                result['current_change'] = current_change_match.group(1).strip()
            
            # 提取文档部分
            document_match = re.search(r'## 文档\s*\n(.*?)(?=\n## |$)', content, re.DOTALL)
            if document_match:
                result['document'] = document_match.group(1).strip()
            
            return result
        except Exception as e:
            self.logger.error(f"解析活动上下文文件内容时出错: {e}")
            return {'header': '', 'current_change': '', 'document': ''}
    
    def _get_active_context_path(self, directory_path: str) -> str:
        """
        获取活动上下文中对应的目录路径
        
        Args:
            directory_path: 原始目录路径
            
        Returns:
            str: 活动上下文中对应的目录路径
        """
        relative_path = os.path.relpath(directory_path, self.source_dir)
        return os.path.join(self.source_dir, ".auto-coder", "active-context", relative_path)
        