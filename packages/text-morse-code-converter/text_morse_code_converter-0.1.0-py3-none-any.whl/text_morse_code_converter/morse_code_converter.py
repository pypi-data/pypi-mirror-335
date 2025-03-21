import time
import sounddevice as sd
import numpy as np

MORSE_CODE_DICT = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    "0": "-----",
    ",": "--..--",
    ".": ".-.-.-",
    "?": "..--..",
    "'": ".----.",
    "/" : "-..-.",
    "(" : "-.--.",
    ")" : "-.--.-",
    ":" : "—...",
    "=" : "-...-",
    "+" : ".-.-.",
    "-" : "-....-",
    "\"" : ".-..-.",
    "@": ".--.-.",
    " ": "/"
}

REVERSE_MORSE_CODE_DICT = {value: key for key, value in MORSE_CODE_DICT.items()}


def text_to_morse(text, play_sound=False):
    text = text.upper()
    morse_code = []

    for char in text:
        if char in MORSE_CODE_DICT:
            morse_code.append(MORSE_CODE_DICT[char])
        else:
            raise ValueError(f"Unsupported character: '{char}'.")

    morse_output = " ".join(morse_code)

    if play_sound:
        play_morse_sound(morse_output)  

    return morse_output


def morse_to_text(morse_code, play_sound=False):
    morse_code = morse_code.strip()
    morse_words = morse_code.split(" / ")
    text = []

    for word in morse_words:
        morse_chars = word.split(" ")
        for morse_char in morse_chars:
            if morse_char in REVERSE_MORSE_CODE_DICT:
                text.append(REVERSE_MORSE_CODE_DICT[morse_char])
            elif morse_char:
                raise ValueError(
                    f"Invalid Morse code: '{morse_char}'. Only valid Morse code patterns are supported."
                )
        text.append(" ")

    if play_sound:
        play_morse_sound(morse_code)

    return "".join(text).strip()


def is_valid_morse(morse_code):
    if not morse_code:
        return False

    morse_words = morse_code.split(" / ")

    for word in morse_words:
        morse_chars = word.split(" ")
        for morse_char in morse_chars:
            # Skip empty strings
            if not morse_char:
                continue
            if morse_char not in REVERSE_MORSE_CODE_DICT and morse_char != "/":
                return False

    return True


def get_morse_alphabet():
    return MORSE_CODE_DICT.copy()


DOT_DURATION = 0.2 
DASH_DURATION = 0.7
FREQUENCY = 800  

def play_morse_sound(morse_code):
    """
    Play Morse code as sound.

    - Dot (.) = Short beep
    - Dash (-) = Long beep
    - Space (' ') = Pause
    """
    for symbol in morse_code:
        if symbol == ".":
            play_beep(DOT_DURATION)
        elif symbol == "-":
            play_beep(DASH_DURATION)
        elif symbol == " ":
            time.sleep(DOT_DURATION) 
        elif symbol == "/":
            time.sleep(DASH_DURATION)  

def play_beep(duration):
    sample_rate = 44100  
    frequency = 250 
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)  
    sd.play(wave, samplerate=sample_rate)
    sd.wait()

