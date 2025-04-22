import json
from pathlib import Path
import sys


def read_pronunciation_config(filepath):
    """
    Read JSON file containing `pronunciation` object
    detailing recommended pronunciation of terms for 
    AI model when generating speech.

    Expected format:
    {
        "pronunciation": {
            "term_1_here": "pronunciation_1_here",
            "term_2_here": "pronunciation_2_here"
        }
    }

    Returns an instruction string to be appended to existing
    instruction string in speech_generator module.
    """

    filepath = Path(filepath)

    if not filepath.is_file():
        print("Provided path to config isn't a filepath. Exiting.")
        sys.exit(1)

    try:
        with filepath.open('r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON format: {e}")

    pronunciation_data = data["pronunciation"]

    if not isinstance(pronunciation_data, dict):
        print("'pronunciation' must be a dictionary.")
        sys.exit(1)
    
    # check that all keys and values are strings
    for key, value in pronunciation_data.items():
        if not isinstance(key, str) or not isinstance(value, str):
            print("All keys and values in 'pronunciation' must be strings.")
            sys.exit(1)
        
    pronunciation_instruction_string = "Pronunciation: please use the following as a guide to pronunciation of key terms. For each of the following items, the string before the colon is the term, and the string after the colon is the phonetic pronunciation:\n"

    for key, value in pronunciation_data.items():
        pronunciation_instruction_string = pronunciation_instruction_string + f"{key}: {value}\n"
    
    return pronunciation_instruction_string
