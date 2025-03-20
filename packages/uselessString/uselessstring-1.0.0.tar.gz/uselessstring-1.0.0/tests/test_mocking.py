import pytest
from src.mocking import mocking  

def test_mocking_case_variation():
    text = "Hello, World!"
    mocked_text = mocking(text)
    assert mocked_text.lower() == text.lower()  

def test_mocking_preserves_length():
    text = "Hello, World!"
    mocked_text = mocking(text)
    assert len(mocked_text) == len(text)  

def test_mocking_different_outputs():
    text = "Hello, World!"
    mocked_text1 = mocking(text)
    mocked_text2 = mocking(text)
    assert mocked_text1 != mocked_text2  

