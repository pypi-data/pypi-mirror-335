![Python build & test](https://github.com/software-students-spring2025/3-python-package-bytebusters/blob/andy/.github/workflows/CI.yaml/badge.svg)

# Morse Code Converter

The Morse Code Converter is a Python package that facilitates the conversion between plain text and Morse code. It offers functionalities to encode text into Morse code and decode Morse code back into readable text. Additionally, it supports file-based conversions, allowing users to process entire files containing text or Morse code.​

## Team members

- [Andy Liu](https://github.com/andy-612)
- [Chenxin Yan](https://github.com/chenxin-yan)
- [Willow](https://github.com/Willow-Zero)
- [Leo Wu](https://github.com/leowu777)

## Features

- **Text to Morse Code Conversion:** Convert any given text into its Morse code representation.​
- **Morse Code to Text Conversion:** Decode Morse code sequences back into plain text.​
- **File Conversion:** Process files to convert their contents between text and Morse code.
- **Morse Code to Audio:** Can play sound for morse code through a combination of long and short beeps.

## Development set up

1. Install Python (3.11+), pipenv, and Git.
2. Navigate to the project folder, start a virtual environment `python -m venv venv`, and activate it by `source venv/bin/activate ` for Mac users or `venv\Scripts\activate` for Windows users.
3. Install dependencies `pip install -r requirements.txt`
4. Run the package using commands below.

## Example commands to run the package

- Example commands for text to morse: `PYTHONPATH=src python -m morse --text "HELLO WORLD"`
- Example commands for morse to text: `PYTHONPATH=src python -m morse --morse ".... . .-.. .-.. --- / .-- --- .-. .-.. -.."`
- Example commands for text input file to morse output file: `PYTHONPATH=src python -m morse --input_file input.txt --output_file output.txt --file_mode text_to_morse`
- Example commands for morse input file to text output file: `PYTHONPATH=src python -m morse --input_file input.txt --output_file output.txt --file_mode morse_to_text`
- Example commands for including a sound output: `PYTHONPATH=src python -m morse --text "HELLO WORLD" --sound`

## Testing

1. Follow steps in development set up .
2. Run `pytest`.

## How to contribute

We welcome contributions from the community. To set up the development environment:

1. Clone this repo.
2. Follow the steps in development set up.
