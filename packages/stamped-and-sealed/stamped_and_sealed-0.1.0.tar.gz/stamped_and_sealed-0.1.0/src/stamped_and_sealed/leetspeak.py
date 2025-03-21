def convert_to_leetspeak(text: str) -> str:
    """
    Converts normal text into leetspeak.
    
    Args: text (str): The input text.
    
    Returns: str: The text converted into leetspeak.
    """
    leet_dict = {
        'a': '4', 'b': '8', 'c': '<', 'd': '|)', 'e': '3',
        'f': '|=', 'g': '6', 'h': '#', 'i': '1', 'j': '_|',
        'k': '|<', 'l': '1', 'm': '/\\/\\', 'n': '|\\|', 'o': '0',
        'p': '|D', 'q': '(,)', 'r': '|2', 's': '5', 't': '7',
        'u': '(_)','v': '\\/', 'w': '\\/\\/', 'x': '}{', 'y': '`/',
        'z': '2'
    }
    
    return ''.join(leet_dict.get(char.lower(), char) for char in text)

