# tests/test_reverse.py
import pytest
from src.reverse import reverse

def test_reverse_simple():
    assert reverse("Hello world") == "world Hello"

def test_reverse_single_word():
    assert reverse("Hello") == "Hello"  # reversing a single word is just the same word

def test_reverse_multiple_words():
    assert reverse("One Two Three") == "Three Two One"