import pytest
from src.echo import echo

VALID_TEXT = "Hello, world!"
VALID_NUM = 5

def test_echo_correct_input():
    """Should pass with valid text and positive integer."""
    expected_output = "Hello, world!Hello, world!Hello, world!Hello, world!Hello, world!"
    
    assert(echo(VALID_TEXT, VALID_NUM) == expected_output)
    
def test_invalid_string_throws_error():
    """Should raise TypeError when text is not a string"""
    invalid_text = 123
    
    with pytest.raises(TypeError):
        echo(invalid_text, VALID_NUM)

def test_invalid_num_throws_error():
    """Should raise TypeError when number is not an integer"""
    invalid_num = "Hello again, world!"
    invalid_float = 3.1415
    
    with pytest.raises(TypeError):
        echo(VALID_TEXT, invalid_num)
    with pytest.raises(TypeError):
        echo(VALID_TEXT, invalid_float)

def test_negative_num_throws_error():
    """Should raise ValueError when number is negative or zero"""
    negative_num = -5
    
    with pytest.raises(ValueError):
        echo(VALID_TEXT, negative_num)
    with pytest.raises(ValueError):
        echo(VALID_TEXT, 0)
