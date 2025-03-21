import argparse
from .file_converter import convert_morse_file
from .morse_code_converter import text_to_morse, morse_to_text

def main():
    parser = argparse.ArgumentParser(description="Morse Code Converter")
    
    parser.add_argument(
        "-t", "--text", help="Convert text to Morse code", type=str
    )
    parser.add_argument(
        "-m", "--morse", help="Convert Morse code to text", type=str
    )
    parser.add_argument(
        "-i", "--input_file", help="Input file path for file conversion"
    )
    parser.add_argument(
        "-o", "--output_file", help="Output file path for file conversion"
    )
    parser.add_argument(
        "--file_mode", choices=["morse_to_text", "text_to_morse"], 
        help="Mode for file conversion"
    )
    parser.add_argument("--sound", action="store_true", help="Play Morse code sound")

    args = parser.parse_args()

    if args.text:
        print(text_to_morse(args.text, play_sound=args.sound))

    elif args.morse:
        print(morse_to_text(args.morse, play_sound=args.sound))

    elif args.input_file and args.output_file and args.file_mode:
        convert_morse_file(args.input_file, args.output_file, args.file_mode)

    else:
        print("Invalid command! Use -h for help.")

if __name__ == "__main__":
    main()
