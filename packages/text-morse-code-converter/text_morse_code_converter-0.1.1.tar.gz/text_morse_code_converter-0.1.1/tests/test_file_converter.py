from src.text_morse_code_converter.file_converter import convert_morse_file

def test_morse_to_text_file_conversion(tmp_path):
    input_file = tmp_path / "morse_input.txt"
    output_file = tmp_path / "text_output.txt"

    input_file.write_text(".... . .-.. .-.. --- / .-- --- .-. .-.. -..")

    convert_morse_file(str(input_file), str(output_file), "morse_to_text")

    assert output_file.read_text().strip() == "HELLO WORLD"

def test_text_to_morse_file_conversion(tmp_path):
    input_file = tmp_path / "text_input.txt"
    output_file = tmp_path / "morse_output.txt"

    input_file.write_text("Hello World")

    convert_morse_file(str(input_file), str(output_file), "text_to_morse")

    assert output_file.read_text().strip() == ".... . .-.. .-.. --- / .-- --- .-. .-.. -.."
