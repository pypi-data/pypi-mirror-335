import pytest
from stamped_and_sealed.fortune_py import generate_fortune, get_random_fortune, format_fortune

def test_fortune_generation():
    default_fortune = generate_fortune()
    assert isinstance(default_fortune, str)
    assert len(default_fortune) > 0
    
    funny_fortune = generate_fortune(theme="funny")
    assert isinstance(funny_fortune, str)
    assert len(funny_fortune) > 0
    
    with pytest.raises(ValueError):
        generate_fortune(theme="nonexistent")
    
    random_fortune = get_random_fortune()
    assert isinstance(random_fortune, str)
    assert len(random_fortune) > 0

def test_fortune_formatting():
    test_message = "Test fortune message"
    
    plain_format = format_fortune(test_message, "plain")
    assert plain_format == test_message
    
    box_format = format_fortune(test_message, "ascii_box")
    assert "+" in box_format
    assert "| Test fortune message |" in box_format
    
    with pytest.raises(ValueError):
        format_fortune(test_message, "invalid_format")

def test_multiline_formatting():
    multiline = "Line 1\nLine 2\nLine 3"
    formatted = format_fortune(multiline, "ascii_box")
    
    assert formatted.count("\n") == 4 
    assert formatted.startswith("+")
    assert "| Line 1 |" in formatted
    assert "| Line 2 |" in formatted
    assert "| Line 3 |" in formatted
    assert formatted.endswith("+")
