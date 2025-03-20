"""
Unit tests for the horoscope module.

Verifies:
    Correctness of zodiac sign and ruling planet.
    Correctness of lucky number calculation.
    Handling of invalid user inputs.
    Reproducibility of generated horoscopes given the same inputs.
    Correctness of zodiac signs on date boundaries.
    Correctness for the leap day edge case.
"""

import pytest
from pykeafortune import horoscope

def test_valid_horoscope():
    """
    Verify get_horoscope returns the correct zodiac sign, ruling planet, and lucky number
    given a valid input.
    """

    birthday = "2000-03-21"
    birth_time = "12:34"
    location = "New York"
    result = horoscope.get_horoscope(birthday, birth_time, location)

    assert isinstance(result, str)
    assert "Your zodiac sign is Aries" in result
    assert "ruled by Mars" in result

    # Calculate expected lucky number: (3*21 + 12*34) % 50 + 1
    # 3*21 = 63, 12*34 = 408, sum = 471, 471 % 50 = 21, plus 1 = 22.
    assert "Your lucky number for today is 22." in result

def test_invalid_birthday_format():
    """
    Verify that get_horoscope raises a ValueError upon receiving
    incorrectly formatted user birthday.
    """

    # If the birthday is not in 'YYY-MM-DD' format, ValueError should be raised.
    with pytest.raises(ValueError, match="Birthday must be in 'YYYY-MM-DD' format."):
        horoscope.get_horoscope("03-21-2000", "12:34", "New York")

def test_invalid_birth_time_format():
    """
    Verify that get_horoscope raises a ValueError upon receiving
    incorrectly formatted user birthtime.
    """

    invalid_times = [
        "12:34:56",
        "12",
        "12:",
        ":34",
        "25:00",
        "12:60",
        "",
    ]
    for invalid_time in invalid_times:
        with pytest.raises(ValueError,
                            match=r"Birth time must be in \'HH:MM\' format \(24-hour clock\)\."):
            horoscope.get_horoscope("2000-03-21", invalid_time, "New York")

def test_empty_location():
    """
    Verify that get_horoscope raises a ValueError upon receiving
    an empty user birth location.
    """

    with pytest.raises(ValueError, match="Location must be a non-empty string."):
        horoscope.get_horoscope("2000-03-21", "12:34", "")

def test_non_string_location():
    """
    Verify that get_horoscope raises a ValueError upon receiving
    invalid location data type.
    """

    with pytest.raises(ValueError, match="Location must be a non-empty string."):
        horoscope.get_horoscope("2000-03-21", "12:34", 123)

def test_reproducibility():
    """
    Verifies consistency of get_horoscope given the same inputs.
    """

    birthday = "2000-03-21"
    birth_time = "12:34"
    location = "New York"
    result1 = horoscope.get_horoscope(birthday, birth_time, location)
    result2 = horoscope.get_horoscope(birthday, birth_time, location)
    assert result1 == result2

def test_zodiac_boundaries():
    """
    Verifies that get_horoscope assigns the correct zodiac sign on date boundaries.
    """

    # Capricorn: Dec 22 to Jan 19.
    result = horoscope.get_horoscope("2000-12-22", "08:00", "Los Angeles")
    assert "Your zodiac sign is Capricorn" in result
    result = horoscope.get_horoscope("2000-01-19", "08:00", "Los Angeles")
    assert "Your zodiac sign is Capricorn" in result

    # Aquarius: Jan 20 to Feb 18.
    result = horoscope.get_horoscope("2000-01-20", "08:00", "Los Angeles")
    assert "Your zodiac sign is Aquarius" in result
    result = horoscope.get_horoscope("2000-02-18", "08:00", "Los Angeles")
    assert "Your zodiac sign is Aquarius" in result

    # Pisces: Feb 19 to Mar 20.
    result = horoscope.get_horoscope("2000-02-19", "08:00", "Los Angeles")
    assert "Your zodiac sign is Pisces" in result
    result = horoscope.get_horoscope("2000-03-20", "08:00", "Los Angeles")
    assert "Your zodiac sign is Pisces" in result

    # Aries: Mar 21 to Apr 19.
    result = horoscope.get_horoscope("2000-03-21", "08:00", "Los Angeles")
    assert "Your zodiac sign is Aries" in result
    result = horoscope.get_horoscope("2000-04-19", "08:00", "Los Angeles")
    assert "Your zodiac sign is Aries" in result

def test_leap_day():
    """
    Verifies get_horoscope correctly deals with leap days.
    """

    # February 29 should be a valid date here (2000 is a leap year).
    result = horoscope.get_horoscope("2000-02-29", "12:00", "Paris")
    # According to the zodiac ranges, Feb 29 falls under Pisces.
    assert "Your zodiac sign is Pisces" in result
