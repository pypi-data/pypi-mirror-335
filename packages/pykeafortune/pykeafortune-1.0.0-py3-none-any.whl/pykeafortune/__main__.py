"""
__main__.py

This module serves as an example of a program that uses all functions in the pykeafortune package
"""

from pykeafortune.fortune_cookie import get_fortune
from pykeafortune.horoscope import get_horoscope
from pykeafortune.lucky_day import get_lucky_day
from pykeafortune.lucky_number import get_lucky_number

def main():
    """Calls every function in the pykeafortune package and prints all function returns."""
    
    print("Welcome to Pykeafortune - Your Personal Fortune Teller!")
    print("-" * 55)

    print("\nLet's first figure out your lucky number!")
    user_favorite_color = input("Enter your favorite color: ")
    user_lucky_number = get_lucky_number(user_favorite_color)

    print("\nYour personal lucky number is ", user_lucky_number, ".", sep="")

    print("\nNow, let's get your personalized horoscope!")

    birthday = input("Enter your birthday (YYYY-MM-DD): ")
    birth_time = input("Enter your birth time (HH:MM): ")
    location = input("Enter your birth location: ")

    horoscope = get_horoscope(birthday, birth_time, location)
    print("\nYour Horoscope:")
    print(horoscope)

    print("\nNow time for your fortune!")
    number = int(input("Pick a number from 1 to 50 (inclusive) for your fortune: "))
    print("\nYour Fortune:")
    print(get_fortune(number))

    print("\nFinally, let's figure out your lucky day!")
    day = input("Enter your favorite day of the week (unabbreviated): ")
    print("\nYour Lucky Day:")
    print(get_lucky_day(day))

if __name__ == "__main__":
    main()
