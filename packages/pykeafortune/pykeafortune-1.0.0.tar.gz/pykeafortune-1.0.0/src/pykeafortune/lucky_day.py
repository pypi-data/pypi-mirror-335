"""
Lucky Day module:

This module returns a lucky day based on the user's favorite day of the week.
"""

import datetime
import random

def get_lucky_day(favorite_day: str) -> datetime.datetime:
    """
    Returns a random future date that occurs on the user's favorite day of the week.

    Parameters:
        favorite_day (str): The user's favorite day of the week (e.g. Monday, Tuesday)

    Returns:
        datetime.date: A datetime.date object for the lucky day.

    Raises:
        ValueError: If the user's favorite day is not a valid day of the week.
        TypeError: If the user input is not a string.
    """

    if not isinstance(favorite_day, str):
        raise TypeError("Argument must be a string, but received a non-string value.")

    favorite_day = favorite_day.lower()
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    if favorite_day not in days:
        raise ValueError("Invalid day entered. Please enter a valid "
                        "day of the week without any abbreviations.")

    today = datetime.date.today()

    current_day = today.weekday()
    target_day = days.index(favorite_day)

    day_offset = (target_day - current_day) % 7

    # Generated lucky day must be in the future
    if day_offset == 0:
        day_offset += 7

    # Generated lucky day occurs within the next 11 weeks,
    # as week_range * 7 + day_offset <= 77
    week_range = random.randint(0, 10)

    lucky_day = today + datetime.timedelta(days=day_offset + (week_range * 7))

    return lucky_day
