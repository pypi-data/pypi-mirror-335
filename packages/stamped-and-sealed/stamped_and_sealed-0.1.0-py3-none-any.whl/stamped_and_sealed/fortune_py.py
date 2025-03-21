import random

# Theme collections
_THEMES = {
    "inspirational": [
        "The journey of a thousand miles begins with a single step.",
        "Your potential is limited only by your imagination.",
        "Believe you can and you're halfway there.",
        "The best way to predict the future is to create it.",
        "Success is not final, failure is not fatal: It is the courage to continue that counts.",
    ],
    "funny": [
        "A balanced diet means a cookie in each hand.",
        "If at first you don't succeed, destroy all evidence that you tried.",
        "The road to success is always under construction.",
        "I find the harder I work, the more luck I have. Coincidence?",
        "Always remember you're unique, just like everyone else.",
    ],
    "programming": [
        "Sometimes it pays to stay in bed on Monday, rather than spending the rest of the week debugging Monday's code.",
        "Premature optimization is the root of all evil.",
        "Programs must be written for people to read, and only incidentally for machines to execute.",
        "Good code is its own best documentation.",
        "First, solve the problem. Then, write the code.",
    ],
}

_CUSTOM_THEMES = {}

def _format_plain(message):
    return message

def _format_ascii_box(message):
    lines = message.split("\n")
    width = max(len(line) for line in lines)
    
    result = ["+" + "-" * (width + 2) + "+"]
    for line in lines:
        result.append("| " + line.ljust(width) + " |")
    result.append("+" + "-" * (width + 2) + "+")
    
    return "\n".join(result)

_FORMATTERS = {
    "plain": _format_plain,
    "ascii_box": _format_ascii_box,
}

def generate_fortune(theme="inspirational"):
    if theme in _THEMES:
        messages = _THEMES[theme]
    elif theme in _CUSTOM_THEMES:
        messages = _CUSTOM_THEMES[theme]
    else:
        raise ValueError(f"Theme '{theme}' not found.")
    
    return random.choice(messages)

def get_random_fortune():
    all_themes = list(_THEMES.keys()) + list(_CUSTOM_THEMES.keys())
    theme = random.choice(all_themes)
    return generate_fortune(theme)

def format_fortune(message, format_type="plain"):
    if format_type not in _FORMATTERS:
        raise ValueError(f"Format type '{format_type}' not supported.")
    
    formatter = _FORMATTERS[format_type]
    return formatter(message)
