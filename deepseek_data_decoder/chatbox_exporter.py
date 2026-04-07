import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from pydantic import BaseModel, Field
from .models import Session, Nodes, Message, Fragment, FragmentType

class ChatboxSession(BaseModel):
    """ChatBox会话格式"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: str = "chat"
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=lambda: {
        "provider": "deepseek",
        "modelId": "deepseek-chat",
        "temperature": 0.7,
        "topP": 1
    })
    threadName: str = ""


class ChatboxExporter:
    """ChatBox格式导出器"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sessions: List[ChatboxSession] = []
    
    def _timestamp_to_ms(self, timestamp_str: str) -> int:
        """将ISO时间戳转换为毫秒时间戳"""
        dt = datetime.fromisoformat(timestamp_str)
        return int(dt.timestamp() * 1000)
    
    def _parse_fragment_content(self, fragment: Fragment) -> str:
        """解析片段内容为文本"""
        content_parts = []
        
        if fragment.type == FragmentType.REQUEST:
            content_parts.append(fragment.content)
        elif fragment.type == FragmentType.RESPONSE:
            content_parts.append(fragment.content)
        elif fragment.type == FragmentType.THINK:
            content_parts.append(f"【思考过程】\n{fragment.content}")
        elif fragment.type == FragmentType.SEARCH:
            if fragment.results:
                content_parts.append("【搜索结果】")
                for i, result in enumerate(fragment.results, 1):
                    content_parts.append(f"{i}. {result.title}")
                    content_parts.append(f"   {result.url}")
                    if result.snippet:
                        content_parts.append(f"   {result.snippet}")
        elif fragment.type == FragmentType.READ_LINK:
            content_parts.append("【读取链接内容】")
        
        return "\n".join(content_parts)
    
    def _parse_message(self, message: Message) -> Dict[str, Any]:
        """解析单条消息为ChatBox格式"""
        # 合并所有片段内容
        content_parts = []
        for fragment in message.fragments:
            content_parts.append(self._parse_fragment_content(fragment))
        
        # 添加文件信息
        if message.files:
            content_parts.append("\n【上传的文件】")
            for file in message.files:
                content_parts.append(f"- {file.file_name}")
        
        content = "\n".join(content_parts)
        
        return {
            "id": str(uuid.uuid4()),
            "role": "assistant" if any(f.type == FragmentType.RESPONSE for f in message.fragments) else "user",
            "contentParts": [{"type": "text", "text": content}],
            "timestamp": self._timestamp_to_ms(message.inserted_at),
            "wordCount": len(content),
            "tokenCount": len(content) // 2,  # 粗略估计
            "aiProvider": "deepseek" if any(f.type == FragmentType.RESPONSE for f in message.fragments) else None,
            "model": message.model if message.model else None,
            "generating": False,
            "status": [],
            "firstTokenLatency": 0,
            "toolCalls": {}
        }
    
    def _traverse_messages(self, session: Session, node_id: str, messages: List[Dict[str, Any]]):
        """遍历消息树"""
        if node_id not in session.mapping:
            return
        
        node = session.mapping[node_id]
        
        # 添加当前节点的消息
        if node.message:
            messages.append(self._parse_message(node.message))
        
        # 递归处理子节点
        for child_id in node.children:
            self._traverse_messages(session, child_id, messages)
    
    def add_session(self, session: Session):
        """添加一个会话到导出列表"""
        chatbox_session = ChatboxSession(
            name=session.title,
            threadName=session.title,
            messages=[]
        )
        
        # 遍历消息树
        if "root" in session.mapping:
            self._traverse_messages(session, "root", chatbox_session.messages)
        
        self.sessions.append(chatbox_session)
    
    def export(self) -> Path:
        """导出所有会话到JSON文件"""
        output_path = self.output_dir / "chatbox_export.json"
        
        # 构建导出数据
        export_data = {
            "__exported_items": ["conversations"],
            "__exported_at": datetime.now().isoformat() + "Z",
            "chat-session-settings": {
                "provider": "deepseek",
                "modelId": "deepseek-chat"
            },
            "chat-sessions-list": [],
            "picture-session-settings": {}
        }
        
        for session in self.sessions:
            session_dict = session.model_dump()
            # 移除不必要的字段
            if "settings" in session_dict:
                session_dict.pop("settings")
            export_data["chat-sessions-list"].append(session_dict)
        
        # 写入文件
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False)
        
        return output_path
    
    def export_single(self, session: Session, output_path: Path) -> Path:
        """导出单个会话到指定路径"""
        chatbox_session = ChatboxSession(
            name=session.title,
            threadName=session.title,
            messages=[]
        )
        
        if "root" in session.mapping:
            self._traverse_messages(session, "root", chatbox_session.messages)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(chatbox_session.model_dump(), f, ensure_ascii=False)
        
        return output_path