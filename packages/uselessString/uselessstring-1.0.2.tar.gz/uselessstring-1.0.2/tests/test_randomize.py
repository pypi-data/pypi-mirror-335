import pytest
from src.randomize import randomize  

def test_randomize_preserves_length():
    text = "Hello, World!"
    randomized_text = randomize(text)
    assert len(randomized_text) == len(text), "Output length must match input length"

def test_randomize_preserves_non_letters():
    text = "Hello, World!"
    randomized_text = randomize(text)
    
    # Ensure punctuation and spaces remain in place
    for i, char in enumerate(text):
        if not char.isalpha():
            assert randomized_text[i] == char, f"Character '{char}' at position {i} should remain unchanged"

def test_randomize_different_outputs():
    text = "Hello, World!"
    randomized_text1 = randomize(text)
    randomized_text2 = randomize(text)

    # The output should be different in most cases since it's randomized
    assert randomized_text1 != randomized_text2, "Randomization should result in different outputs most of the time"

def test_randomize_same_letters():
    text = "HelloWorld"
    randomized_text = randomize(text)
    
    # Ensure all original letters exist in the new string
    assert sorted(randomized_text) == sorted(text), "Output must contain the same letters as input"

def test_randomize_empty_string():
    text = ""
    assert randomize(text) == "", "Empty string should return empty string"

def test_randomize_single_character():
    text = "A"
    assert randomize(text) == "A", "Single character should remain unchanged"

