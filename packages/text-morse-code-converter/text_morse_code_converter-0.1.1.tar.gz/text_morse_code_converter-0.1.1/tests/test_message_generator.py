from src.text_morse_code_converter.message_generator import generate_message

def test_generate_message():
    text = "HELLO"
    expected_output = ".... . .-.. .-.. ---" 
    assert generate_message(text) == expected_output

    assert generate_message("") == ""

    text_with_special_chars = "HELLO 123"
    expected_output_special = ".... . .-.. .-.. --- / .---- ..--- ...--"
    assert generate_message(text_with_special_chars) == expected_output_special
