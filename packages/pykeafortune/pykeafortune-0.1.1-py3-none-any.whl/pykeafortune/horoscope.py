"""
Horoscope module:

This module returns a horoscope based on the user's birthday, birth time, and location of birth.
"""

import datetime
import random

def get_horoscope(birthday: str, birth_time: str, location: str) -> str:
    """
    Returns a horoscope based on the user's birthday, birth time, and location of birth.

    Parameters:
        birthday (str): The birthday in 'YYYY-MM-DD' format.
        birth_time (str): The birth time in 'HH:MM' format (24-hour clock).
        location (str): The location of birth (e.g., city, country).

    Returns:
        str: A generated horoscope string.

    Raises:
        ValueError: If the birthday or birth_time is not in the correct format,
                    or if location is empty.
    """

    try:
        birth_date = datetime.datetime.strptime(birthday, '%Y-%m-%d')
    except ValueError as exc:
        raise ValueError("Birthday must be in 'YYYY-MM-DD' format.") from exc

    try:
        # First check if the birth_time matches the exact format we want
        if not birth_time or len(birth_time.split(':')) != 2:
            raise ValueError("Birth time must be in 'HH:MM' format (24-hour clock).")

        # Then try to parse it to validate the values
        datetime.datetime.strptime(birth_time, '%H:%M')
    except ValueError as exc:
        raise ValueError("Birth time must be in 'HH:MM' format (24-hour clock).") from exc

    if not location or not isinstance(location, str):
        raise ValueError("Location must be a non-empty string.")

    month = birth_date.month
    day = birth_date.day

    zodiac = _get_zodiac_sign(month, day)

    ruling_planets = {
        'Aries': 'Mars',
        'Taurus': 'Venus',
        'Gemini': 'Mercury',
        'Cancer': 'Moon',
        'Leo': 'Sun',
        'Virgo': 'Mercury',
        'Libra': 'Venus',
        'Scorpio': 'Pluto',
        'Sagittarius': 'Jupiter',
        'Capricorn': 'Saturn',
        'Aquarius': 'Uranus',
        'Pisces': 'Neptune'
    }
    ruling_planet = ruling_planets.get(zodiac, 'Unknown')

    # We calculate a lucky number based on birthdate and time
    hour, minute = map(int, birth_time.split(':'))
    lucky_number = (month * day + hour * minute) % 50 + 1

    horoscope_base = {
        'Aries': "A day of bold decisions and fresh energy awaits you.",
        'Taurus': "Stability and comfort are on the horizon, along with unexpected indulgence.",
        'Gemini': "Your wit and curiosity will lead you to new connections.",
        'Cancer': "Emotional clarity and nurturing moments will define your day.",
        'Leo': "Your charisma shines through; expect admiration and creative breakthroughs.",
        'Virgo': "A focus on detail and practical approaches will yield rewards.",
        'Libra': "Harmony and balance come with opportunities for social growth.",
        'Scorpio': "Passion and intensity fuel your pursuits; trust your instincts.",
        'Sagittarius': "Adventure and optimism drive your journey; embrace new experiences.",
        'Capricorn': "Discipline and ambition pave the way for success in your endeavors.",
        'Aquarius': "Innovation and independence inspire you to think outside the box.",
        'Pisces': "Empathy and imagination are your strengths; let your creativity flow."
    }
    base_message = horoscope_base.get(zodiac, "The cosmos holds endless possibilities for you.")

    # We set a seed here so we can reproduce the same
    # horoscope using a combination of birth date and time
    random.seed(int(birth_date.strftime('%Y%m%d')) + hour + minute)

    personalized_advice = random.choice([
        "Today is a perfect day to embrace change.",
        "You may find unexpected opportunities around every corner.",
        "Your intuition is strong; trust it and act accordingly.",
        "A challenge may arise, but your resilience will see you through.",
        "An encounter with someone new could alter your perspective."
    ])

    final_sentences = [
        f"Also, the energy in {location} aligns perfectly with your spirit.",
        f"However, the cosmic forces advise you to avoid {location} today."
    ]
    final_sentence = random.choice(final_sentences)

    horoscope = (
        f"Your zodiac sign is {zodiac}, ruled by {ruling_planet}. "
        f"{base_message} {personalized_advice} "
        f"Your lucky number for today is {lucky_number}. "
        f"{final_sentence}"
    )

    return horoscope

def _get_zodiac_sign(month: int, day: int) -> str:
    """
    Returns a zodiac sign determined by birth month and birth day.

    Parameters:
        month (int): Birth month (1-12)
        day (int): Birth day (1-31)

    Returns:
        str: The associated zodiac sign.
    """

    if (month == 12 and day >= 22) or (month == 1 and day <= 19):
        zodiac = 'Capricorn'
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        zodiac = 'Aquarius'
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        zodiac = 'Pisces'
    elif (month == 3 and day >= 21) or (month == 4 and day <= 19):
        zodiac = 'Aries'
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        zodiac = 'Taurus'
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        zodiac = 'Gemini'
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        zodiac = 'Cancer'
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        zodiac = 'Leo'
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        zodiac = 'Virgo'
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        zodiac = 'Libra'
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        zodiac = 'Scorpio'
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        zodiac = 'Sagittarius'
    else:
        zodiac = 'Unknown'

    return zodiac
