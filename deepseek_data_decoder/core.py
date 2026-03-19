import orjson
from zipfile import ZipFile
from pathlib import Path
from .models import Session
from .parse_args import Args
from .load_format_package import load_format_package
from .parser import ParseSession
from jinja2.sandbox import SandboxedEnvironment
import re

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
    
    def sanitize_filename(self, filename: str) -> str:
        sanitized = self.illegal_chars.sub("_", filename)
        if len(sanitized) > 200:
            sanitized = sanitized[:200]
        return sanitized.strip()
    
    def decode(self, path: str | Path):
        file_name_template = self.template_env.from_string(self._args.file_name)
        dir_name_template = self.template_env.from_string(self._args.dir_name)
        with ZipFile(path, "r") as zip_file:
            conversations = orjson.loads(zip_file.read("conversations.json"))
            
            for conversation in conversations:
                session = Session(**conversation)
                
                safe_name = self.sanitize_filename(session.title)

                dir_name = dir_name_template.render(
                    dir_name = safe_name,
                    inserted_at = session.inserted_time(),
                    updated_at = session.updated_time(),
                )

                if not dir_name:
                    dir_name = f"session_{session.id[-8:]}"
                
                session_output_dir = Path(self._args.output) / dir_name
                session_output_dir.mkdir(parents=True, exist_ok=True)
                
                # 解析会话，生成所有路径文件
                for i, parsed in enumerate(self._parse_session.parse(session)):
                    # 生成文件名
                    if i == 0:
                        # 第一条路径（通常是root链）命名为 "0000-{会话标题}.md"
                        file_name = f"0000-{safe_name}.md"
                    else:
                        # 其他路径按顺序编号
                        file_name = f"{i:04d}-{safe_name}.md"
                    
                    output_path = session_output_dir / file_name
                    
                    file_name = file_name_template.render(
                        file_name = file_name,
                        inserted_at = parsed.inserted_at,
                        updated_at = parsed.updated_at,
                    )
                    
                    with open(output_path, "w", encoding="utf-8") as file:
                        file.write(parsed.text)
                    
                    print(f"Decoded: {dir_name}/{file_name}")