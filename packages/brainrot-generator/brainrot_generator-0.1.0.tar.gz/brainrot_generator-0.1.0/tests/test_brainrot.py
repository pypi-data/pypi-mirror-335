import pytest
import random
import string
from brainrot.brainrot_functions import (
    brainrot,
    get_brain_rot_of,
    random_capitalization,
    rotify, 
    backwards_text,
    brainrot_list  # import the list for reference in tests
)

# TESTS FOR BRAINROT(N)
def test_brainrot_non_positive():
    # if n<=0, brainrot returns empty dictionary 
    assert brainrot(-1) == {}

def test_brainrot_returns_correct_number():
    # brainrot returns exactlt n entries if n within bounds
    n = 3
    result = brainrot(n)
    expected_len = min(n, len(brainrot_list))
    assert len(result) == expected_len
    for key in result:
        assert key in brainrot_list

def test_brainrot_exceeds_list_length():
    # if n is greater than list entries, return max available entries
    n = len(brainrot_list) + 10
    result = brainrot(n)
    expected = len(brainrot_list)
    assert len(result) == expected


#TESTS FOR RANDOM_CAPITALIZATION(PHRASE)
def test_random_capitalization_basic():
    # tests if capitalization is properly converted
    input_str = "hello"
    expected = "hElLo"
    assert random_capitalization(input_str) == expected

def test_random_capitalization_empty():
    # empty string returns empty string
    assert random_capitalization("") == ""

def test_random_capitalization_single_char():
    # test behavior for single character, should remain the same
    letter = random.choice(string.ascii_letters)
    assert random_capitalization(letter) == letter

#TESTS FOR BACKWARDS_TEXT(TEXT)
def test_backwards_text_regular():
    #reverse text in string
    input_text = "Hello"
    expected = "olleH"
    assert backwards_text(input_text) == expected

def test_backwards_text_empty():
    # reverse empty text
    input_text = ""
    expected = ""
    assert backwards_text(input_text) == expected

def test_backwards_text_non_string():
    # reverse number text
    input_value = 12345
    expected = "54321"
    assert backwards_text(input_value) == expected

def test_backwards_text_special_characters():
    # text with non-alphabetical and numbers
    input_text = "A!B@C#"
    expected = "#C@B!A"
    assert backwards_text(input_text) == expected