from .morse_code_converter import text_to_morse

def generate_message(text, play_sound=False, save_to_file=None):
  
    morse_code = text_to_morse(text, play_sound=play_sound)

    if save_to_file:
        with open(save_to_file, "w", encoding="utf-8") as f:
            f.write(morse_code)
        print(f"Generated Morse code saved to '{save_to_file}'")
   
    return morse_code