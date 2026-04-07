# deepseek_data_decoder.py
from deepseek_data_decoder import Decoder, ParseArgs

def main():
    argparser = ParseArgs()
    argparser.init_args()
    args = argparser.parse_args()
    
    print(f"Input file: {args.input}")
    print(f"Format Package: {args.format}")
    print(f"Output file: {args.output}")
    print(f"Output format: {'ChatBox JSON' if args.chatbox else 'Markdown'}")
    print("-" * 50)
    
    decoder = Decoder(args)
    decoder.decode(args.input)

if __name__ == "__main__":
    main()