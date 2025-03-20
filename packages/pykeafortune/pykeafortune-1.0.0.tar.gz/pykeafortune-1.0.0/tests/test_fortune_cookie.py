"""
Unit tests for the fortune_cookie module.

Verifies:
    Correctness of generated fortunes for each type of fortune.
    Handling of invalid user inputs.
"""

import pytest
from pykeafortune import fortune_cookie

def test_big_fortune():
    """
    Verify get_fortune returns a valid big fortune given valid user input.
    """

    big_fortune_messages = [
        "Great luck is in the future!",
        "A surprise windfall is coming your way!",
        "Your hard work will soon pay off!",
        "Exciting opportunities are on the horizon!",
        "Love and success will find you!"
        "Happy life is just in front of you!"
        "A golden egg of opportunity falls into your lap this month!"
        "The universe is aligning in your favor — expect something wonderful!"
        "Your confidence and determination will lead to great success!"
        "Love, wealth, and happiness are all heading your way!"
        "An exciting adventure awaits you—embrace it with open arms!"
        "Your positive energy will attract incredible opportunities!"
    ]

    fortune = fortune_cookie.get_fortune(1)
    assert fortune.startswith("Big Fortune: ")
    assert fortune.replace("Big Fortune: ", "") in big_fortune_messages

def test_mid_fortune():
    """
    Verify get_fortune returns a valid mid fortune given valid user input.
    """

    mid_fortune_messages = [
        "Things are stable, keep pushing forward.",
        "A steady path leads to success.",
        "You will find balance in your endeavors.",
        "A small victory will brighten your day.",
        "Stay patient; rewards are on the way."
        "Go take a rest; you deserve it."
        "It’s time to get moving. Your spirits will lift accordingly."
        "The best way to predict the future is to create it."
        "An opportunity is coming, but you must stay prepared."
        "You are in a good place, but there's still work to do."
        "Small victories are still victories — learn to appreciate them."
        "Stay adaptable—things will change, but you are ready."
        "Now is a time for patience, not haste."
    ]

    fortune = fortune_cookie.get_fortune(50)
    assert fortune.startswith("Mid Fortune: ")
    assert fortune.replace("Mid Fortune: ", "") in mid_fortune_messages

def test_small_fortune():
    """
    Verify get_fortune returns a valid small fortune given valid user input.
    """

    small_fortune_messages = [
        "A lesson will soon be learned the hard way.",
        "Patience is needed in difficult times.",
        "You may face obstacles, but you will overcome them.",
        "Not every day is sunny, but the storm will pass."
        "Don’t confuse recklessness with confidence."
        "A gambler not only will lose what he has, but also will lose what he doesn’t have."
        "404 Fortune Not Found..."
        "The one you love may not love you back."
        "Stop procrastinating. The inability to make a decision will become your downfall."
        "Caution is advised — think before making decisions."
        "Not everything will go as planned, but you’ll find your way."
        "Even in difficult times, new opportunities may appear."
        "A tough situation will soon reveal an important lesson."
        "Do not allow material possessions to steer your happiness."
    ]

    fortune = fortune_cookie.get_fortune(4)
    assert fortune.startswith("Small Fortune: ")
    assert fortune.replace("Small Fortune: ", "") in small_fortune_messages

def test_invalid_number():
    """
    Verify that get_fortune raises a ValueError upon receiving
    an invalid number.
    """

    invalid = [100, 51, -14, -100, 0]

    for number in invalid:
        with pytest.raises(ValueError, match="Invalid integer entered. "
            "Please enter an integer between 1 and 50, inclusive."):
            fortune_cookie.get_fortune(number)

def test_invalid_input_type():
    """
    Verify that get_fortune raises a TypeError upon receiving
    an invalid input type.
    """

    invalid = ["abc", "x", 1.5, -10.001]

    for test_input in invalid:
        with pytest.raises(TypeError, match="Argument must be an int, "
            "but received a non-int value."):
            fortune_cookie.get_fortune(test_input)
