# deepseek_data_decoder/parse_args.py
import argparse
from pydantic import BaseModel, Field

class Args(BaseModel):
    input: str = ""
    format: str = ""
    output: str = ""
    file_name: str = ""
    dir_name: str = ""
    chatbox: bool = False
    cb: bool = False  # 简写别名

class ParseArgs:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="DeepSeek Data Decoder")
        
    def init_args(self):
        self.parser.add_argument("-i", "--input", type=str, help="Input file path")
        self.parser.add_argument("-f", "--format", type=str, help="Format package file path")
        self.parser.add_argument("-o", "--output", type=str, help="Output dir path")
        self.parser.add_argument("-fn", "--file-name", type=str, default="{{file_name}}", help="Output file name template")
        self.parser.add_argument("-dn", "--dir-name", type=str, default="{{dir_name}}", help="Output dir name template")
        self.parser.add_argument("-cb", "--chatbox", action="store_true", help="Export to ChatBox JSON format")
    
    def parse_args(self) -> Args:
        args = self.parser.parse_args()
        return Args(
            input=args.input,
            format=args.format,
            output=args.output,
            file_name=args.file_name,
            dir_name=args.dir_name,
            chatbox=args.chatbox,
            cb=args.chatbox  # 同步别名
        )