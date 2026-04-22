# deepseek_data_decoder/chatbox_exporter.py
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from pydantic import BaseModel, Field
from .models import Session, Nodes, Message, Fragment, FragmentType

class ChatboxSession(BaseModel):
    """ChatBox session format"""
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
    """ChatBox format exporter"""
    
    def __init__(self, output_dir: Path, by_date: bool = False, date_format: str = "%Y-%m-%d"):
        """
        Initialize exporter
        
        Args:
            output_dir: Output directory path
            by_date: Whether to organize output by date
            date_format: Date format string, default %Y-%m-%d
        """
        self.output_dir = Path(output_dir)
        self.by_date = by_date
        self.date_format = date_format
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sessions: List[ChatboxSession] = []
        self._session_count = 0
    
    def _timestamp_to_ms(self, timestamp_str: str) -> int:
        """Convert ISO timestamp to milliseconds timestamp"""
        dt = datetime.fromisoformat(timestamp_str)
        return int(dt.timestamp() * 1000)
    
    def _get_session_date(self, session: Session) -> str:
        """Get session date for grouping"""
        dt = session.updated_time()
        return dt.strftime(self.date_format)
    
    def _parse_fragment_content(self, fragment: Fragment) -> str:
        """Parse fragment content to text"""
        content_parts = []
        
        if fragment.type == FragmentType.REQUEST:
            content_parts.append(fragment.content)
        elif fragment.type == FragmentType.RESPONSE:
            content_parts.append(fragment.content)
        elif fragment.type == FragmentType.THINK:
            content_parts.append(f"[Thinking Process]\n{fragment.content}")
        elif fragment.type == FragmentType.SEARCH:
            if fragment.results:
                content_parts.append("[Search Results]")
                for i, result in enumerate(fragment.results, 1):
                    content_parts.append(f"{i}. {result.title}")
                    content_parts.append(f"   URL: {result.url}")
                    if result.snippet:
                        content_parts.append(f"   Snippet: {result.snippet}")
        elif fragment.type == FragmentType.READ_LINK:
            content_parts.append("[Link Content]")
        
        return "\n".join(content_parts)
    
    def _parse_message(self, message: Message) -> Dict[str, Any]:
        """Parse single message to ChatBox format"""
        content_parts = []
        for fragment in message.fragments:
            content_parts.append(self._parse_fragment_content(fragment))
        
        if message.files:
            content_parts.append("\n[Uploaded Files]")
            for file in message.files:
                content_parts.append(f"- {file.file_name}")
        
        content = "\n".join(content_parts)
        
        # Determine message role
        is_assistant = any(f.type == FragmentType.RESPONSE for f in message.fragments)
        
        msg = {
            "id": str(uuid.uuid4()),
            "role": "assistant" if is_assistant else "user",
            "contentParts": [{"type": "text", "text": content}],
            "timestamp": self._timestamp_to_ms(message.inserted_at),
            "wordCount": len(content),
            "tokenCount": len(content) // 2,
            "generating": False,
            "status": [],
            "firstTokenLatency": 0,
            "toolCalls": {}
        }
        
        if is_assistant and message.model:
            msg["aiProvider"] = "deepseek"
            msg["model"] = message.model
        
        return msg
    
    def _traverse_messages(self, session: Session, node_id: str, messages: List[Dict[str, Any]]):
        """Traverse message tree"""
        if node_id not in session.mapping:
            return
        
        node = session.mapping[node_id]
        
        if node.message:
            messages.append(self._parse_message(node.message))
        
        for child_id in node.children:
            self._traverse_messages(session, child_id, messages)
    
    def add_session(self, session: Session):
        """Add a session to export list"""
        chatbox_session = ChatboxSession(
            name=session.title,
            threadName=session.title,
            messages=[]
        )
        
        if "root" in session.mapping:
            self._traverse_messages(session, "root", chatbox_session.messages)
        
        self.sessions.append(chatbox_session)
        self._session_count += 1
    
    def export(self) -> Path:
        """Export all sessions to JSON file"""
        if not self.by_date:
            return self._export_single_file()
        else:
            return self._export_by_date()
    
    def _export_single_file(self) -> Path:
        """Export as single file"""
        output_path = self.output_dir / "chatbox_export.json"
        
        export_data = self._build_export_data(self.sessions)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def _export_by_date(self) -> Path:
        """Export by date subdirectories"""
        sessions_by_date: Dict[str, List[ChatboxSession]] = {}
        
        # Note: This requires original Session objects for date grouping
        # For now, fallback to single file mode
        print("[ChatBox] Warning: Date-based export requires original Session objects. Falling back to single file mode.")
        return self._export_single_file()
    
    def _build_export_data(self, sessions: List[ChatboxSession]) -> Dict[str, Any]:
        """Build export data structure"""
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
        
        for session in sessions:
            session_dict = session.model_dump()
            export_data["chat-sessions-list"].append(session_dict)
        
        return export_data