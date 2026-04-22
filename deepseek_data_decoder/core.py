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
        
        # Grouping mode: 'day', 'month', 'year', or None
        self._group_mode = None
        if getattr(args, 'group_day', False):
            self._group_mode = 'day'
        elif getattr(args, 'group_month', False):
            self._group_mode = 'month'
        elif getattr(args, 'group_year', False):
            self._group_mode = 'year'
    
    def _get_group_key(self, dt) -> str:
        """Get grouping key based on mode"""
        if self._group_mode == 'day':
            return dt.strftime("%Y-%m-%d")
        elif self._group_mode == 'month':
            return dt.strftime("%Y-%m")
        elif self._group_mode == 'year':
            return dt.strftime("%Y")
        return None
    
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
        """Export to ChatBox JSON format with optional grouping (day/month/year)"""
        output_dir = Path(self._args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Group sessions by date if enabled
        sessions_by_group: Dict[str, List[Session]] = {}
        
        with ZipFile(path, "r") as zip_file:
            conversations = orjson.loads(zip_file.read("conversations.json"))
            total = len(conversations)
            
            mode_names = {'day': 'day', 'month': 'month', 'year': 'year'}
            mode_name = mode_names.get(self._group_mode, 'none')
            print(f"[ChatBox] Loading {total} conversation(s) (group mode: {mode_name})...")
            
            for conversation in conversations:
                session = Session(**conversation)
                
                if self._group_mode:
                    group_key = self._get_group_key(session.updated_time())
                    if group_key not in sessions_by_group:
                        sessions_by_group[group_key] = []
                    sessions_by_group[group_key].append(session)
                else:
                    # Single file mode: collect all sessions
                    exporter = ChatboxExporter(output_dir, by_date=False)
                    exporter.add_session(session)
            
            if self._group_mode:
                # Group-based export mode
                group_count = len(sessions_by_group)
                print(f"[ChatBox] Group-based export mode enabled, {group_count} group(s) found")
                
                for group_key, group_sessions in sessions_by_group.items():
                    group_dir = output_dir / group_key
                    group_dir.mkdir(parents=True, exist_ok=True)
                    
                    exporter = ChatboxExporter(group_dir, by_date=False)
                    for session in group_sessions:
                        exporter.add_session(session)
                    
                    output_path = exporter.export()
                    print(f"[ChatBox] Exported {len(group_sessions)} session(s) to: {group_key}/chatbox_export.json")
                
                # Generate summary file with all sessions
                all_exporter = ChatboxExporter(output_dir, by_date=False)
                for sessions in sessions_by_group.values():
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