import pytest
import random
import string
from src.brainrot.brainrot_functions import (
    brainrot,
    get_brain_rot_of,
    random_capitalization,
    rotify, 
    backwards_text,
    generate_brain_rot,
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

# TESTS FOR GET_BRAINROT_OF(NAME)
def test_get_brainrot_regular():
    input = "haliey welch"
    expected = "haliey welch: hawk tuah, spit on that thang"
    assert get_brain_rot_of(input) == expected

def test_get_brainrot_empty():
    # check empty input
    input = ""
    expected = " is unfortunately not a brainrot contributor"
    assert get_brain_rot_of(input) == expected

def test_get_brainrot_rand_capitalisation():
    # check capitalised input
    input = "bRo"
    expected = "bro: The typa shi bro sends when ___"
    assert get_brain_rot_of(input) == expected

def test_get_brainrot_not_instance():
    # check capitalised input
    input = "br0"
    expected = "br0 is unfortunately not a brainrot contributor"
    assert get_brain_rot_of(input) == expected

# TEST FOR ROTIFY(STRING)
def test_rotify_regular():
    #check regular input
    input = "hello"
    expected = "hello ahh"
    assert rotify(input) == expected

def test_rotify_empty():
    input = ""
    expected = " ahh"
    assert rotify(input) == expected

def test_rotify_non_string():
    input = 12345
    expected = "12345 ahh"
    assert rotify(input) == expected

# TEST FOR GENERATE_BRAIN_ROT(N)
def test_generate_brain_rot_regular():
    # Test for a regular input where n is within the bounds
    n = 10  # Change this number based on the expected average length of strings in brainrot_list values if needed
    result = generate_brain_rot(n)
    # Count words in the result
    word_count = len(result.split())
    assert word_count == n, f"Expected {n} words, but got {word_count} words."

def test_generate_brain_rot_not_num():
    n = "hi"
    assert generate_brain_rot(n) == "Input value is not an integer"

def test_generate_brain_rot_zero():
    # Test for zero input, expecting an empty string
    assert generate_brain_rot(0) == "No brainrot to be returned"