"""
Lucky Number module:

This module returns a lucky number based on the user's favorite color.
"""

def get_lucky_number(favorite_color: str) -> int:
    """
    Returns a lucky number determined by the user's favorite color.

    Parameters:
        favorite_color (str): The user's favorite color (e.g. blue, red)

    Returns:
        int: An integer representing the user's lucky number

    Raises:
        ValueError: If the user's favorite color does not exist in color -> number map
        TypeError: If the user input is not a string.
    """

    if not isinstance(favorite_color, str):
        raise TypeError("Argument must be a string, but received a non-string value.")

    favorite_color = favorite_color.lower()

    colors = {
        "red": 101,
        "dark red": 245,
        "light red": 312,
        "blue": 220,
        "dark blue": 399,
        "light blue": 145,
        "green": 88,
        "dark green": 330,
        "light green": 176,
        "yellow": 455,
        "dark yellow": 312,
        "light yellow": 78,
        "orange": 232,
        "dark orange": 389,
        "light orange": 157,
        "purple": 267,
        "dark purple": 413,
        "light purple": 192,
        "pink": 305,
        "hot pink": 444,
        "light pink": 138,
        "brown": 189,
        "dark brown": 402,
        "light brown": 215,
        "black": 499,
        "gray": 266,
        "dark gray": 390,
        "light gray": 111,
        "white": 10,
        "cyan": 180,
        "dark cyan": 288,
        "light cyan": 92,
        "magenta": 322,
        "dark magenta": 440,
        "light magenta": 156,
        "teal": 239,
        "dark teal": 368,
        "light teal": 132,
        "lavender": 208,
        "beige": 280,
        "ivory": 98,
        "maroon": 376,
        "navy": 410,
        "gold": 312,
        "silver": 170,
        "peach": 256,
        "turquoise": 193,
        "olive": 322,
        "coral": 266,
        "rose": 287,
    }

    if favorite_color not in colors:
        raise ValueError("Invalid color entered. Please enter a valid, "
                        "more common color.")

    return colors[favorite_color]
