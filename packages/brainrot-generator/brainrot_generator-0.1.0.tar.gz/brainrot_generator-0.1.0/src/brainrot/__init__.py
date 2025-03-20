"""
Brain Rot  - A Python package for those who brainrot.

This package provides functions to help you better understand 
and generate brain rot: 

- `hall_of_fame(n)`: Returns `n` random names of hall of fame brain rotters.
- `random_capitalization(phrase)`: Randomly capitalizes letters in a given phrase.
- `rotify(input_string)`: Appends "ahh" to the end of a string for rot.
- `brainrot(n)`: Returns `n` random brain rot quotes from the collection.
- `get_brain_rot_of(name)`: Returns a random brain rot quote from a specific contributor.
- `backwards_text(text)`: Returns the input text reversed.
- `generate_brain_rot(word_counter)`: Generates brain rot text with specified number of words.

"""

from .brainrot_functions import (
    brainrot,
    get_brain_rot_of,
    random_capitalization,
    rotify,
    backwards_text,
    generate_brain_rot
)