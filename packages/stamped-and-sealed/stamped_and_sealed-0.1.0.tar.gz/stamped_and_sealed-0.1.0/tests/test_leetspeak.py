import pytest
from stamped_and_sealed.leetspeak import convert_to_leetspeak

def test_basic_words():
    assert convert_to_leetspeak("hello") == "#3110"
    assert convert_to_leetspeak("leet") == "1337"

def test_mixed_case():
    assert convert_to_leetspeak("PyThOn") == "|D`/7#0|\\|"

def test_special_characters():
    assert convert_to_leetspeak("code!") == "<0|)3!"

def test_empty_string():
    assert convert_to_leetspeak("") == ""

def test_numbers_unchanged():
    assert convert_to_leetspeak("1234") == "1234"

if __name__ == "__main__":
    pytest.main()
