"""
Unit tests for the lucky_number module.

Verifies:
    Correctness of generated lucky number.
    Case-insensitivity of logic.
    Handling of invalid user inputs.
    Reproducibility of generated lucky numbers given the same inputs.
"""

import pytest
from pykeafortune import lucky_number

def test_valid_lucky_number():
    """
    Verify get_lucky_number returns a valid lucky number as an integer
    between 0 and 500 given valid user input.
    """

    favorite_color = "blue"
    result = lucky_number.get_lucky_number(favorite_color)

    assert isinstance(result, int)
    assert 0 <= result <= 500

def test_case_insensitive():
    """
    Verify get_lucky_number returns a valid lucky number 
    regardless of capitalization of user input.
    """

    result_one = lucky_number.get_lucky_number("DARK red")
    result_two = lucky_number.get_lucky_number("orangE")
    result_three = lucky_number.get_lucky_number("pInK")

    assert isinstance(result_one, int)
    assert isinstance(result_two, int)
    assert isinstance(result_three, int)

    assert 0 <= result_one <= 500
    assert 0 <= result_two <= 500
    assert 0 <= result_three <= 500

def test_invalid_color():
    """
    Verify that get_lucky_number raises a ValueError upon receiving
    an invalid color.
    """

    invalid = ["mint", "crimson", "salmon", "", "123", "__"]

    for color in invalid:
        with pytest.raises(ValueError, match="Invalid color entered. "
            "Please enter a valid, more common color."):
            lucky_number.get_lucky_number(color)

def test_invalid_input_type():
    """
    Verify that get_lucky_number raises a TypeError upon receiving
    an invalid input type.
    """

    invalid = [1, 1.4, -134, 5]

    for test_input in invalid:
        with pytest.raises(TypeError, match="Argument must be a string, "
            "but received a non-string value."):
            lucky_number.get_lucky_number(test_input)

def test_reproducibility():
    """
    Verifies consistency of get_lucky_number given the same inputs.
    """

    favorite_color = "green"
    result_one = lucky_number.get_lucky_number(favorite_color)
    result_two = lucky_number.get_lucky_number(favorite_color)
    assert result_one == result_two
