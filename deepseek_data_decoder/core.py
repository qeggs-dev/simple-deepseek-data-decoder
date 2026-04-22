# deepseek_data_decoder/core.py
import orjson
from zipfile import ZipFile
from pathlib import Path
from .models import Session
from .parse_args import Args
from .load_format_package import load_format_package
from .parser import ParseSession
from .chatbox_exporter import ChatboxExporter
from jinja2.sandbox import SandboxedEnvironment
import re
from typing import Dict, List

class Decoder:
    def __init__(self, args: Args):
        self._args = args
        self._parse_session = ParseSession(
            load_format_package(
                args.format
            )
        )
        self.illegal_chars = re.compile(r"[^\w\d]", re.UNICODE)
        self.template_env = SandboxedEnvironment()
        self._export_to_chatbox = getattr(args, 'chatbox', False) or getattr(args, 'cb', False)
        self._export_by_date = getattr(args, 'by_date', False) or getattr(args, 'date', False)
    
    def sanitize_filename(self, filename: str) -> str:
        sanitized = self.illegal_chars.sub("_", filename)
        if len(sanitized) > 200:
            sanitized = sanitized[:200]
        return sanitized.strip()
    
    def decode(self, path: str | Path):
        """Main entry point for decoding"""
        if self._export_to_chatbox:
            return self._decode_to_chatbox(path)
        return self._decode_to_markdown(path)
    
    def _decode_to_markdown(self, path: str | Path):
        """Export to Markdown format (original logic)"""
        file_name_template = self.template_env.from_string(self._args.file_name)
        dir_name_template = self.template_env.from_string(self._args.dir_name)
        
        with ZipFile(path, "r") as zip_file:
            conversations = orjson.loads(zip_file.read("conversations.json"))
            
            total = len(conversations)
            print(f"[Markdown] Processing {total} conversation(s)...")
            
            for idx, conversation in enumerate(conversations, 1):
                session = Session(**conversation)
                
                safe_name = self.sanitize_filename(session.title)

                dir_name = dir_name_template.render(
                    dir_name=safe_name,
                    inserted_at=session.inserted_time(),
                    updated_at=session.updated_time(),
                )

                if not dir_name:
                    dir_name = f"session_{session.id[-8:]}"
                
                session_output_dir = Path(self._args.output) / dir_name
                session_output_dir.mkdir(parents=True, exist_ok=True)
                
                # Parse session, generate all path files
                for i, parsed in enumerate(self._parse_session.parse(session)):
                    # Generate filename
                    if i == 0:
                        file_name = f"0000-{safe_name}.md"
                    else:
                        file_name = f"{i:04d}-{safe_name}.md"
                    
                    output_path = session_output_dir / file_name
                    
                    file_name = file_name_template.render(
                        file_name=file_name,
                        inserted_at=parsed.inserted_at,
                        updated_at=parsed.updated_at,
                    )
                    
                    with open(output_path, "w", encoding="utf-8") as file:
                        file.write(parsed.text)
                    
                    print(f"[Markdown] [{idx}/{total}] Exported: {dir_name}/{file_name}")
    
    def _decode_to_chatbox(self, path: str | Path):
        """Export to ChatBox JSON format with optional date-based grouping"""
        output_dir = Path(self._args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Group sessions by date if enabled
        sessions_by_date: Dict[str, List[Session]] = {}
        
        with ZipFile(path, "r") as zip_file:
            conversations = orjson.loads(zip_file.read("conversations.json"))
            total = len(conversations)
            
            print(f"[ChatBox] Loading {total} conversation(s)...")
            
            for conversation in conversations:
                session = Session(**conversation)
                
                if self._export_by_date:
                    date_key = session.updated_time().strftime("%Y-%m-%d")
                    if date_key not in sessions_by_date:
                        sessions_by_date[date_key] = []
                    sessions_by_date[date_key].append(session)
                else:
                    # Single file mode: collect all sessions
                    exporter = ChatboxExporter(output_dir, by_date=False)
                    exporter.add_session(session)
            
            if self._export_by_date:
                # Date-based export mode
                date_count = len(sessions_by_date)
                print(f"[ChatBox] Date-based export mode enabled, {date_count} date group(s) found")
                
                for date_key, date_sessions in sessions_by_date.items():
                    date_dir = output_dir / date_key
                    date_dir.mkdir(parents=True, exist_ok=True)
                    
                    exporter = ChatboxExporter(date_dir, by_date=False)
                    for session in date_sessions:
                        exporter.add_session(session)
                    
                    output_path = exporter.export()
                    print(f"[ChatBox] Exported {len(date_sessions)} session(s) to: {date_key}/chatbox_export.json")
                
                # Generate summary file with all sessions
                all_exporter = ChatboxExporter(output_dir, by_date=False)
                for sessions in sessions_by_date.values():
                    for session in sessions:
                        all_exporter.add_session(session)
                all_output = all_exporter.export()
                print(f"[ChatBox] Summary file exported to: {all_output}")
                
            else:
                # Single file export mode
                exporter = ChatboxExporter(output_dir, by_date=False)
                for conversation in conversations:
                    session = Session(**conversation)
                    exporter.add_session(session)
                
                output_path = exporter.export()
                print(f"[ChatBox] Export completed: {output_path}")
                print(f"[ChatBox] Total sessions: {len(conversations)}")