"""
活动包 - 生成目录的活动上下文文档
"""

from typing import Dict, Any, Optional, Tuple, List
import os
import sys
import re
import byzerllm
from loguru import logger as global_logger

class ActivePackage:
    """
    ActivePackage负责生成每个目录的活动上下文文档，
    包括当前变更信息和相关文件的详细文档。
    
    如果目录中已存在active.md文件，会先读取现有内容作为参考，
    然后基于现有信息和新信息一起生成更新后的文档。
    """
    
    def __init__(self, llm: byzerllm.ByzerLLM):
        """
        初始化活动包生成器
        
        Args:
            llm: ByzerLLM实例，用于生成文档内容
        """
        self.llm = llm
        # 创建专用的 logger 实例
        self.logger = global_logger.bind(name="ActivePackage")
        
    def generate_active_file(self, context: Dict[str, Any], query: str, 
                            existing_file_path: Optional[str] = None, 
                            file_changes: Optional[Dict[str, Tuple[str, str]]] = None) -> str:
        """
        生成完整的活动文件内容
        
        Args:
            context: 目录上下文字典
            query: 用户查询/需求
            existing_file_path: 可选的现有文件路径，如果提供，将读取并参考现有内容
            file_changes: 文件变更字典，键为文件路径，值为(变更前内容, 变更后内容)的元组
            
        Returns:
            str: 生成的活动文件内容
        """
        try:
            # 检查是否有现有文件
            existing_content = None
            if existing_file_path and os.path.exists(existing_file_path):
                try:
                    with open(existing_file_path, 'r', encoding='utf-8') as f:
                        existing_content = f.read()
                    self.logger.info(f"Found existing active.md file: {existing_file_path}")
                except Exception as e:
                    self.logger.error(f"Error reading existing file {existing_file_path}: {e}")
            
            # 增强上下文信息，添加文件变更信息
            enhanced_context = self._enhance_context_with_changes(context, file_changes)
            
            # 根据是否有现有内容选择不同的生成方式
            if existing_content:
                # 有现有内容，使用更新模式
                file_content = self.generate_updated_active_file(enhanced_context, query, existing_content)
            else:
                # 无现有内容，使用创建模式
                file_content = self.generate_new_active_file(enhanced_context, query)
            
            return file_content
        except Exception as e:
            self.logger.error(f"Error generating active file: {e}")
            return f"# 生成文档时出错\n\n错误: {str(e)}"
    
    def _enhance_context_with_changes(self, context: Dict[str, Any], 
                                    file_changes: Optional[Dict[str, Tuple[str, str]]]) -> Dict[str, Any]:
        """
        使用文件变更信息增强上下文
        
        Args:
            context: 原始上下文字典
            file_changes: 文件变更字典
            
        Returns:
            Dict[str, Any]: 增强后的上下文字典
        """
        if not file_changes:
            return context
        
        # 创建上下文的深拷贝，避免修改原始内容
        enhanced_context = context.copy()
        
        # 添加文件变更信息到changed_files
        if 'changed_files' in enhanced_context:
            changed_files_with_diffs = []
            for file_info in enhanced_context['changed_files']:
                file_path = file_info['path']
                # 创建文件信息的副本
                new_file_info = file_info.copy()
                
                # 添加变更内容（如果有）
                if file_path in file_changes:
                    before_content, after_content = file_changes[file_path]
                    new_file_info['before_content'] = before_content
                    new_file_info['after_content'] = after_content
                    new_file_info['has_diff'] = True
                
                changed_files_with_diffs.append(new_file_info)
            
            enhanced_context['changed_files'] = changed_files_with_diffs
        
        # 在上下文中添加文件变更摘要信息
        file_diffs = []
        for file_path, (before, after) in file_changes.items():
            if before and after:
                # 简单计算差异 - 实际应用中可能需要更复杂的差异计算
                diff_info = {
                    'path': file_path,
                    'type': 'modified',
                    'before_lines': len(before.split('\n')) if before else 0,
                    'after_lines': len(after.split('\n')) if after else 0
                }
            elif not before and after:
                diff_info = {'path': file_path, 'type': 'added'}
            elif before and not after:
                diff_info = {'path': file_path, 'type': 'deleted'}
            else:
                continue
                
            file_diffs.append(diff_info)
        
        enhanced_context['file_diffs'] = file_diffs
        
        return enhanced_context
    
    def generate_new_active_file(self, context: Dict[str, Any], query: str) -> str:
        """
        生成全新的活动文件内容
        
        Args:
            context: 目录上下文字典
            query: 用户查询/需求
            
        Returns:
            str: 新生成的活动文件内容
        """
        try:
            # 1. 生成current change部分
            current_change = self.generate_current_change.with_llm(self.llm).run(context, query)
            
            # 2. 生成document部分
            document = self.generate_document.with_llm(self.llm).run(context, query)
            
            # 3. 组合成完整的活动文件内容
            file_content = f"# 活动上下文 - {os.path.basename(context['directory_path'])}\n\n"
            file_content += f"## 当前变更\n\n{current_change}\n\n"
            file_content += f"## 文档\n\n{document}\n"
            
            return file_content
        except Exception as e:
            self.logger.error(f"Error generating new active file: {e}")
            raise
    
    def extract_sections(self, content: str) -> Tuple[str, str, str]:
        """
        从现有内容中提取标题、当前变更和文档部分
        
        Args:
            content: 现有文件内容
            
        Returns:
            Tuple[str, str, str]: 标题部分、当前变更部分、文档部分
        """
        # 默认值
        header = "# 活动上下文\n\n"
        current_change_section = ""
        document_section = ""
        
        try:
            # 提取标题部分（到第一个二级标题之前）
            header_match = re.search(r'^(.*?)(?=\n## )', content, re.DOTALL)
            if header_match:
                header = header_match.group(1).strip() + "\n\n"
            
            # 提取当前变更部分
            current_change_match = re.search(r'## 当前变更\s*\n(.*?)(?=\n## |$)', content, re.DOTALL)
            if current_change_match:
                current_change_section = current_change_match.group(1).strip()
            
            # 提取文档部分
            document_match = re.search(r'## 文档\s*\n(.*?)(?=\n## |$)', content, re.DOTALL)
            if document_match:
                document_section = document_match.group(1).strip()
                
            return header, current_change_section, document_section
        except Exception as e:
            self.logger.error(f"Error extracting sections: {e}")
            return header, current_change_section, document_section
    
    def generate_updated_active_file(self, context: Dict[str, Any], query: str, existing_content: str) -> str:
        """
        基于现有内容生成更新后的活动文件内容
        
        Args:
            context: 目录上下文字典
            query: 用户查询/需求
            existing_content: 现有文件内容
            
        Returns:
            str: 更新后的活动文件内容
        """
        try:
            # 1. 从现有内容中提取各个部分
            header, existing_current_change, existing_document = self.extract_sections(existing_content)
            
            # 2. 分别更新每个部分
            updated_current_change = self.update_current_change.with_llm(self.llm).run(
                context=context,
                query=query,
                existing_current_change=existing_current_change
            )
            
            updated_document = self.update_document.with_llm(self.llm).run(
                context=context,
                query=query,
                existing_document=existing_document
            )
            
            # 3. 组合成更新后的活动文件内容
            file_content = f"{header}"
            file_content += f"## 当前变更\n\n{updated_current_change}\n\n"
            file_content += f"## 文档\n\n{updated_document}\n"
            
            return file_content
        except Exception as e:
            self.logger.error(f"Error updating active file: {e}")
            # 如果更新失败，回退到生成新文档
            self.logger.info("Falling back to generating new active file")
            return self.generate_new_active_file(context, query)
    
    @byzerllm.prompt()
    def update_current_change(self, context: Dict[str, Any], query: str, existing_current_change: str) -> str:
        """
        请基于现有的"当前变更"文档和新的变更信息，生成一个更新后的"当前变更"部分。
        
        现有的"当前变更"内容：
        ```
        {{ existing_current_change }}
        ```
        
        当前需求：
        {{ query }}
        
        目录：{{ context.directory_path }}
        
        最新变更的文件：
        {% for file in context.changed_files %}
        - {{ file.path }}
        {% endfor %}
        
        {% if context.file_diffs %}
        文件变更摘要：
        {% for diff in context.file_diffs %}
        - {{ diff.path }}: {% if diff.type == 'modified' %}修改 (从{{ diff.before_lines }}行到{{ diff.after_lines }}行){% elif diff.type == 'added' %}新增{% elif diff.type == 'deleted' %}删除{% endif %}
        {% endfor %}
        {% endif %}
        
        {% if context.changed_files and context.changed_files[0].has_diff %}
        变更前后的代码对比：
        {% for file in context.changed_files %}
        {% if file.has_diff %}
        文件: {{ file.path }}
        变更前:
        ```
        {{ file.before_content }}
        ```
        
        变更后:
        ```
        {{ file.after_content }}
        ```
        {% endif %}
        {% endfor %}
        {% endif %}
        
        请执行以下任务：
        1. 保留现有文档中的有用历史信息
        2. 添加最新的变更信息，重点描述当前需求相关的变更
        3. 明确指出新的变更与之前变更的关系（如继续完善、修复问题、新增功能等）
        4. 确保变更描述清晰、具体，并表明每个文件的变更内容和目的
        5. 如果有冲突的信息，优先保留最新的信息
        
        你的回答应该是一个完整的"当前变更"部分内容，不需要包含标题。
        """
    
    @byzerllm.prompt()
    def update_document(self, context: Dict[str, Any], query: str, existing_document: str) -> str:
        """
        请基于现有的"文档"部分和新的变更信息，生成一个更新后的"文档"部分。
        
        现有的"文档"内容：
        ```
        {{ existing_document }}
        ```
        
        当前需求：
        {{ query }}
        
        目录：{{ context.directory_path }}
        
        相关文件：
        {% for file in context.changed_files %}
        - {{ file.path }}
        {% endfor %}
        
        {% if context.current_files %}
        当前目录中的其他相关文件：
        {% for file in context.current_files %}
        - {{ file.path }}
        {% endfor %}
        {% endif %}
        
        {% if context.file_diffs %}
        文件变更摘要：
        {% for diff in context.file_diffs %}
        - {{ diff.path }}: {% if diff.type == 'modified' %}修改 (从{{ diff.before_lines }}行到{{ diff.after_lines }}行){% elif diff.type == 'added' %}新增{% elif diff.type == 'deleted' %}删除{% endif %}
        {% endfor %}
        {% endif %}
        
        {% if context.changed_files and context.changed_files[0].has_diff %}
        变更前后的代码对比：
        {% for file in context.changed_files %}
        {% if file.has_diff %}
        文件: {{ file.path }}
        变更前:
        ```
        {{ file.before_content }}
        ```
        
        变更后:
        ```
        {{ file.after_content }}
        ```
        {% endif %}
        {% endfor %}
        {% endif %}
        
        请执行以下任务：
        1. 保留现有文档中的准确信息
        2. 更新每个文件的文档，反映最新的变更
        3. 如果有新文件，为其创建完整的文档
        4. 确保文档格式一致性，每个文件的文档包含：功能、关键组件、变更影响、与其他文件的关系
        5. 如有冲突信息，优先保留最新信息，但保留历史上下文
        
        格式应为：
        
        ### [文件名]
        - **功能**：
        - **关键组件**：
        - **变更影响**：
        - **关系**：
        
        你的回答应该是一个完整的"文档"部分内容，不需要包含标题。
        """
    
    @byzerllm.prompt()
    def generate_current_change(self, context: Dict[str, Any], query: str) -> str:
        """
        请分析下面的代码变更，并描述它们与当前需求的关系。
        
        需求：
        {{ query }}
        
        目录：{{ context.directory_path }}
        
        变更的文件：
        {% for file in context.changed_files %}
        - {{ file.path }}
        {% endfor %}
        
        {% if context.file_diffs %}
        文件变更摘要：
        {% for diff in context.file_diffs %}
        - {{ diff.path }}: {% if diff.type == 'modified' %}修改 (从{{ diff.before_lines }}行到{{ diff.after_lines }}行){% elif diff.type == 'added' %}新增{% elif diff.type == 'deleted' %}删除{% endif %}
        {% endfor %}
        {% endif %}
        
        {% if context.changed_files and context.changed_files[0].has_diff %}
        变更前后的代码对比：
        {% for file in context.changed_files %}
        {% if file.has_diff %}
        文件: {{ file.path }}
        变更前:
        ```
        {{ file.before_content }}
        ```
        
        变更后:
        ```
        {{ file.after_content }}
        ```
        {% endif %}
        {% endfor %}
        {% endif %}
        
        分析并描述这些变更如何满足需求，以及这个目录中的文件在整体变更中起到什么作用。
        描述应该清晰、具体，并表明每个文件的变更内容和目的。
        """
    
    @byzerllm.prompt()
    def generate_document(self, context: Dict[str, Any], query: str) -> str:
        """
        请为下面列出的每个文件生成详细的文档说明。
        
        需求：
        {{ query }}
        
        目录：{{ context.directory_path }}
        
        文件列表：
        {% for file in context.changed_files %}
        - {{ file.path }}
        {% endfor %}
        
        {% if context.current_files %}
        当前目录中的其他相关文件：
        {% for file in context.current_files %}
        - {{ file.path }}
        {% endfor %}
        {% endif %}
        
        {% if context.file_diffs %}
        文件变更摘要：
        {% for diff in context.file_diffs %}
        - {{ diff.path }}: {% if diff.type == 'modified' %}修改 (从{{ diff.before_lines }}行到{{ diff.after_lines }}行){% elif diff.type == 'added' %}新增{% elif diff.type == 'deleted' %}删除{% endif %}
        {% endfor %}
        {% endif %}
        
        {% if context.changed_files and context.changed_files[0].has_diff %}
        变更前后的代码对比：
        {% for file in context.changed_files %}
        {% if file.has_diff %}
        文件: {{ file.path }}
        变更前:
        ```
        {{ file.before_content }}
        ```
        
        变更后:
        ```
        {{ file.after_content }}
        ```
        {% endif %}
        {% endfor %}
        {% endif %}
        
        对于每个文件，请提供：
        1. 文件的主要功能
        2. 文件中的关键组件（类、函数等）
        3. 此次变更对文件的影响（如果适用）
        4. 文件与其他文件的关系
        
        格式应为：
        
        ### [文件名]
        - **功能**：
        - **关键组件**：
        - **变更影响**：
        - **关系**：
        """ 