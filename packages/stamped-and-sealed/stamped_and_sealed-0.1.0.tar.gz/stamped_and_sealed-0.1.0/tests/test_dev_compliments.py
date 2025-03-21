# tests/test_dev_compliments.py
import unittest
from unittest.mock import patch
import sys
import os
# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from stamped_and_sealed.dev_compliments import dev_compliment
class TestDevCompliments(unittest.TestCase):
    @patch('builtins.print')
    def test_dev_compliment_debugging(self, mock_print):
        dev_compliment("debugging")
        mock_print.assert_called_once()
        output = mock_print.call_args[0][0]
        self.assertIn(output, [
            "You're a debugging pro!",
            "Your problem-solving skills are off the charts!",
            "Bugs fear you!",
            "You squash bugs like a pro!"
        ])
    @patch('builtins.print')
    def test_dev_compliment_coding(self, mock_print):
        dev_compliment("coding")
        mock_print.assert_called_once()
        output = mock_print.call_args[0][0]
        self.assertIn(output, [
            "Your code is so clean, even linting tools take the day off!",
            "You optimize like a Big O genius!",
            "Every line of your code radiates brilliance!",
            "Your code is a masterpiece in the making!"
        ])
    @patch('builtins.print')
    def test_dev_compliment_motivation(self, mock_print):
        dev_compliment("motivation")
        mock_print.assert_called_once()
        output = mock_print.call_args[0][0]
        self.assertIn(output, [
            "What you're coding is legendary!",
            "Keep going! You're bringing your ideas to life!",
            "Every line of code is a step closer to greatness!",
            "You're turning ideas into reality!",
            "You always know how to git things done!",
            "You're building something amazing! Keep pushing forward!"
        ])
    @patch('builtins.print')
    def test_dev_compliment_invalid_category(self, mock_print):
        dev_compliment("invalid_category")
        mock_print.assert_called_once_with(
            "Invalid category: 'invalid_category'. Please choose from: debugging, coding, motivation"
        )
if __name__ == '__main__':
    unittest.main()

