"""
Unit tests for the lucky_day module.

Verifies:
    Correctness of generated lucky day.
    Case-insensitivity of logic.
    Generated lucky day falls within the allowed timeframe.
    Handling of invalid user inputs.
    Generated lucky day is at least a week in the future if favorite_day is today
"""

import datetime
import pytest
from pykeafortune import lucky_day

def test_valid_lucky_day():
    """
    Verify get_lucky_day returns a valid lucky day in the 
    future given valid user input.
    """

    favorite_day = "Monday"
    result = lucky_day.get_lucky_day(favorite_day)

    assert isinstance(result, datetime.date)
    assert result > datetime.date.today()
    assert result.weekday() == 0

def test_case_insensitive():
    """
    Verify get_lucky_day returns a valid lucky day in the future 
    regardless of capitalization of user input.
    """

    result_one = lucky_day.get_lucky_day("monday")
    result_two = lucky_day.get_lucky_day("MONDAY")
    result_three = lucky_day.get_lucky_day("MoNdAy")

    assert isinstance(result_one, datetime.date)
    assert isinstance(result_two, datetime.date)
    assert isinstance(result_three, datetime.date)

    assert result_one > datetime.date.today()
    assert result_two > datetime.date.today()
    assert result_three > datetime.date.today()

    assert result_one.weekday() == 0
    assert result_two.weekday() == 0
    assert result_three.weekday() == 0

def test_valid_timeframe():
    """
    Verify get_lucky_day returns a lucky day within the next
    11 weeks, which is the allowed time frame.
    """

    result = lucky_day.get_lucky_day("Monday")

    today = datetime.date.today()
    date_boundary = today + datetime.timedelta(weeks=11)

    assert today < result <= date_boundary

def test_invalid_day():
    """
    Verify that get_lucky_day raises a ValueError upon receiving
    an invalid day.
    """

    invalid = ["mon", "Th", "123", "", "mondaymonday", "FR1day"]

    for day in invalid:
        with pytest.raises(ValueError, match="Invalid day entered. "
            "Please enter a valid day of the week without any abbreviations."):
            lucky_day.get_lucky_day(day)

def test_invalid_input_type():
    """
    Verify that get_lucky_day raises a TypeError upon receiving
    an invalid input type.
    """

    invalid = [1, 1.4, -134, 5]

    for test_input in invalid:
        with pytest.raises(TypeError, match="Argument must be a string, "
            "but received a non-string value."):
            lucky_day.get_lucky_day(test_input)

def test_favorite_day_today():
    """
    Verify that if user's favorite day is today, then get_lucky_day returns a date
    at least a week in the future.
    """

    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    today = datetime.date.today()
    current_day_index = today.weekday()
    current_day = days[current_day_index]

    result = lucky_day.get_lucky_day(current_day)

    assert result >= today + datetime.timedelta(days=7)
