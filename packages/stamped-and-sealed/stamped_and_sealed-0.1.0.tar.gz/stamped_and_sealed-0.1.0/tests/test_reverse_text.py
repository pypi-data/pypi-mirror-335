import pytest
from my_fun_package.reverse_text import reverse_text

def test_basic_reversal():
    assert reverse_text("hello") == "olleh"

def test_reversal_with_spaces():
    assert reverse_text("hello world") == "dlrow olleh"

def test_ignore_spaces():
    assert reverse_text("hello world", ignore_spaces=True) == "dlrowolleh"

def test_ignore_punctuation():
    assert reverse_text("hello, world!", ignore_punctuation=True) == "dlrow olleh"

def test_empty_string():
    assert reverse_text("") == ""
