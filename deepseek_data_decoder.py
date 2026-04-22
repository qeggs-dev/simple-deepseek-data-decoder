import os
from deepseek_data_decoder import Decoder, ParseArgs

def print_dividing_line():
    print("=" * os.get_terminal_size().columns)

def main():
    argparser = ParseArgs()
    argparser.init_args()
    args = argparser.parse_args()
    print_dividing_line()
    print("DeepSeek Data Decoder")
    print_dividing_line()
    print(f"Input file:  {args.input}")
    print(f"Format pkg:  {args.format}")
    print(f"Output dir:  {args.output}")
    print(f"Export mode: {'ChatBox JSON' if args.chatbox else 'Markdown files'}")
    if args.chatbox and getattr(args, 'by_date', False):
        print(f"Date grouping: Enabled")
    print_dividing_line()
    
    decoder = Decoder(args)
    decoder.decode(args.input)
    
    print_dividing_line()
    print("Decoding completed!")
    print_dividing_line()

if __name__ == "__main__":
    main()