import argparse
from pydantic import BaseModel

class Args(BaseModel):
    input: str = ""
    format: str = ""
    output: str = ""
    file_name: str = ""
    dir_name: str = ""

class ParseArgs:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="DeepSeek Data Decoder")
        
    def init_args(self):
        self.parser.add_argument("-i", "--input", type=str, help="Input file path")
        self.parser.add_argument("-f", "--format", type=str, help="Format package file path")
        self.parser.add_argument("-o", "--output", type=str, help="Output dir path")
        self.parser.add_argument("-fn", "--file-name", type=str, default="{{file_name}}", help="Output file name template")
        self.parser.add_argument("-dn", "--dir-name", type=str, default="{{dir_name}}", help="Output dir name template")
    
    def parse_args(self) -> Args:
        args = self.parser.parse_args()
        return Args(
            input = args.input,
            format = args.format,
            output = args.output,
            file_name = args.file_name,
            dir_name = args.dir_name,
        )