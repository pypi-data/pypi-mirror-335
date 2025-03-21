import os
from .morse_code_converter import text_to_morse, morse_to_text

def convert_morse_file(input_file, output_file, mode="morse_to_text"):
    """
    Reads a file, converts its content, and writes the result to another file.

    :param input_file: Path to the input file.
    :param output_file: Path to the output file.
    :param mode: Conversion mode ('morse_to_text' or 'text_to_morse').
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file '{input_file}' does not exist.")

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if mode == "morse_to_text":
        converted_content = morse_to_text(content)
    elif mode == "text_to_morse":
        converted_content = text_to_morse(content)
    else:
        raise ValueError("Invalid mode! Use 'morse_to_text' or 'text_to_morse'.")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(converted_content)

    print(f"Conversion successful! Output saved to '{output_file}'")
