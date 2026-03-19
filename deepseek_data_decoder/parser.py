from .models import (
    Session,
    File,
    Nodes,
    Message,
    Fragment,
    FragmentType
)
from .format_pkg import FormatPackage
from jinja2.sandbox import SandboxedEnvironment
from pydantic import BaseModel
from datetime import datetime
from typing import Generator, List, Optional

class ParsedSession(BaseModel):
    name: str
    text: str
    inserted_at: datetime
    updated_at: datetime

class ParseSession:
    def __init__(self, format_package: FormatPackage):
        self.template_env = SandboxedEnvironment()
        self.session_template = self.template_env.from_string(format_package.session)
        self.node_template = self.template_env.from_string(format_package.node)
        self.file_template = self.template_env.from_string(format_package.file)
        self.message_template = self.template_env.from_string(format_package.message)
        self.thinking_template = self.template_env.from_string(format_package.thinking)
        self.read_link_template = self.template_env.from_string(format_package.read_link)
        self.user_input_template = self.template_env.from_string(format_package.user_input)
        self.ai_answer_template = self.template_env.from_string(format_package.ai_answer)
        self.search_template = self.template_env.from_string(format_package.search)
        self.search_unit_template = self.template_env.from_string(format_package.search_unit)
    
    def parse_files(self, files: List[File]) -> list[str]:
        """处理文件列表"""
        files_content = []
        for file in files:
            files_content.append(
                self.file_template.render(
                    id = file.id,
                    file_name = file.file_name
                )
            )
        return files_content
    
    def parse_fragment(self, fragment: Fragment) -> str:
        match fragment.type:
            case FragmentType.REQUEST:
                text = self.user_input_template.render(
                    content = fragment.content,
                )
            case FragmentType.RESPONSE:
                text = self.ai_answer_template.render(
                    content = fragment.content,
                )
            case FragmentType.THINK:
                text = self.thinking_template.render(
                    content = fragment.content,
                )
            case FragmentType.SEARCH:
                results: list[str] = []
                for result in fragment.results:
                    results.append(
                        self.search_unit_template.render(
                            url = result.url,
                            title = result.title,
                            snippet = result.snippet,
                            cite_index = result.cite_index,
                            published_at = str(result.published_at),
                            site_name = result.site_name,
                            site_icon = result.site_icon,
                            query_indexes = result.query_indexes,
                            is_hidden = result.is_hidden
                        )
                    )
                text = self.search_template.render(
                    results = results,
                )
            case FragmentType.READ_LINK:
                text = self.read_link_template.render()
            case _:
                text = ""
        return text
    
    def parse_message(self, message: Message | None) -> str:
        """解析单个消息，返回渲染后的字符串"""
        if message is None:
            return ""
            
        fragments_string: list[str] = []
        for fragment in message.fragments:
            fragments_string.append(
                self.parse_fragment(fragment)
            )
        
        return self.message_template.render(
            files = self.parse_files(message.files),
            model = message.model,
            inserted_at = message.inserted_time(),
            fragments_content = fragments_string,
        )

    def parse_chain_nodes(self, nodes: List[Nodes]) -> list[str]:
        """解析一条链上的所有节点，返回合并后的内容"""
        chain_content: list[str] = []
        for node in nodes:
            if node.message:
                chain_content.append(self.parse_message(node.message))
        
        return chain_content

    def find_all_paths(self, session: Session) -> List[List[str]]:
        """找到从root到所有叶子节点的路径"""
        if "root" not in session.mapping:
            return []
        
        paths = []
        
        def dfs(current_id: str, current_path: List[str]):
            # 添加当前节点到路径
            current_path.append(current_id)
            
            # 获取当前节点
            node = session.mapping[current_id]
            
            # 如果没有子节点，说明是叶子节点，保存路径
            if not node.children:
                paths.append(current_path.copy())
            else:
                # 递归遍历所有子节点
                for child_id in node.children:
                    if child_id in session.mapping:  # 确保子节点存在
                        dfs(child_id, current_path)
            
            # 回溯
            current_path.pop()
        
        # 从root开始DFS
        dfs("root", [])
        
        return paths

    def parse(self, session: Session) -> Generator[ParsedSession, None, None]:
        """解析会话，为每条路径生成一个文件"""
        
        # 找到所有路径
        paths = self.find_all_paths(session)
        
        for i, path_ids in enumerate(paths):
            # 获取路径上的所有节点
            path_nodes = []
            for node_id in path_ids:
                if node_id in session.mapping:
                    path_nodes.append(session.mapping[node_id])
            
            if not path_nodes:
                continue
            
            # 生成路径名称（用于文件名）
            if len(path_ids) > 1:
                # 排除root，用节点ID的后几位组成路径名
                path_suffix = "-".join([id[-8:] for id in path_ids[1:] if id])  # 取ID后8位
                chain_name = f"{session.title}-{path_suffix}"
            else:
                chain_name = session.title
            
            inserted_at = session.inserted_time()
            updated_at = session.updated_time()
            
            # 渲染会话模板
            session_text = self.session_template.render(
                id = session.id,
                title = session.title,
                inserted_at = inserted_at,
                updated_at = updated_at,
                chain_content = self.parse_chain_nodes(path_nodes),
                nodes = path_nodes,
            )
            
            yield ParsedSession(
                name = chain_name,
                text = session_text,
                inserted_at = inserted_at,
                updated_at = updated_at,
            )