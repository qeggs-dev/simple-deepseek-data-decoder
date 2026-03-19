from deepseek_data_decoder import Decoder, ParseArgs

def main():
    argparser = ParseArgs()
    argparser.init_args()
    args = argparser.parse_args()
    decoder = Decoder(args)
    decoder.decode(args.input)

if __name__ == "__main__":
    main()