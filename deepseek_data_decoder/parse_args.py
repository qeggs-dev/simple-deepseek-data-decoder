# deepseek_data_decoder/parse_args.py
import argparse
from pydantic import BaseModel

class Args(BaseModel):
    input: str = ""
    format: str = ""
    output: str = ""
    file_name: str = "{{file_name}}"
    dir_name: str = "{{dir_name}}"
    chatbox: bool = False
    cb: bool = False
    group_day: bool = False
    group_month: bool = False
    group_year: bool = False


class ParseArgs:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="DeepSeek Data Decoder",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Export to Markdown (default)
  python deepseek_data_decoder.py -i data.zip -f format.zip -o ./output

  # Export to ChatBox JSON
  python deepseek_data_decoder.py -i data.zip -f format.zip -o ./output -cb

  # Export by day (creates subdirs: 2024-01-15/, 2024-01-16/, ...)
  python deepseek_data_decoder.py -i data.zip -f format.zip -o ./output -cb --day

  # Export by month (creates subdirs: 2024-01/, 2024-02/, ...)
  python deepseek_data_decoder.py -i data.zip -f format.zip -o ./output -cb --month

  # Export by year (creates subdirs: 2024/, 2025/, ...)
  python deepseek_data_decoder.py -i data.zip -f format.zip -o ./output -cb --year
            """
        )
        
    def init_args(self):
        self.parser.add_argument("-i", "--input", type=str, required=True, help="Input file path")
        self.parser.add_argument("-f", "--format", type=str, required=True, help="Format package file path")
        self.parser.add_argument("-o", "--output", type=str, required=True, help="Output dir path")
        self.parser.add_argument("-fn", "--file-name", type=str, default="{{file_name}}", help="Output file name template")
        self.parser.add_argument("-dn", "--dir-name", type=str, default="{{dir_name}}", help="Output dir name template")
        self.parser.add_argument("-cb", "--chatbox", action="store_true", help="Export to ChatBox JSON format")
        
        # Grouping options (mutually exclusive)
        group_group = self.parser.add_mutually_exclusive_group()
        group_group.add_argument("-d", "--day", action="store_true", dest="group_day", 
                                  help="Group by day (creates YYYY-MM-DD directories)")
        group_group.add_argument("-m", "--month", action="store_true", dest="group_month", 
                                  help="Group by month (creates YYYY-MM directories)")
        group_group.add_argument("-y", "--year", action="store_true", dest="group_year", 
                                  help="Group by year (creates YYYY directories)")
    
    def parse_args(self) -> Args:
        args = self.parser.parse_args()
        return Args(
            input=args.input,
            format=args.format,
            output=args.output,
            file_name=args.file_name,
            dir_name=args.dir_name,
            chatbox=args.chatbox,
            cb=args.chatbox,
            group_day=args.group_day,
            group_month=args.group_month,
            group_year=args.group_year
        )