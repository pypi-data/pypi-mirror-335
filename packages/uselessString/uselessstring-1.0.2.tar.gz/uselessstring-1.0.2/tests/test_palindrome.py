import pytest
from src.palindrome import palindrome

def test_reverse_characters():
    input_str = "Hello, world!"
    expected = "!dlrow ,olleH"
    assert palindrome(input_str) == expected

def test_reverse_palindrome():
    # Reversing a palindrome should yield the same string
    input_str = "racecar"
    expected = "racecar"
    assert palindrome(input_str) == expected

def test_reverse_empty_string():
    # Reversing an empty string should return an empty string
    assert palindrome("") == ""

def test_reverse_numeric_string():
    # Reversing a numeric string, such as "1881", should work as expected
    input_str = "1881"
    expected = "1881"
    assert palindrome(input_str) == expected

def test_reverse_sentence():
    # Reversing a sentence letter-by-letter
    input_str = "Able was I ere I saw Elba"
    expected = "ablE was I ere I saw elbA"
    assert palindrome(input_str) == expected
