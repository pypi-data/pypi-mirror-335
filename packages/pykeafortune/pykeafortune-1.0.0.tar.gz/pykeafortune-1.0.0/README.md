[![Build/Test](https://github.com/software-students-spring2025/3-python-package-pyke-ult/actions/workflows/test.yml/badge.svg)](https://github.com/software-students-spring2025/3-python-package-pyke-ult/actions/workflows/test.yml)

# pykeafortune

## Description

[pykeafortune](https://pypi.org/project/pykeafortune/) is a Python package containing functions to find your horoscope, lucky day, lucky number, and fortune cookie fortune when you want to boost your luck and discover any upcoming fortune.

## Installation: How to Import and Use pykeafortune

1. Install the package

        pip install pykeafortune

2. Import desired functions into your Python code

        from pykeafortune.fortune_cookie import get_fortune
        from pykeafortune.horoscope import get_horoscope
        from pykeafortune.lucky_day import get_lucky_day
        from pykeafortune.lucky_number import get_lucky_number


## Documentation

### get_fortune(number: int) -> str

Returns a fortune cookie fortune determined by the passed integer.

Parameters:
- number (int): Any integer such that 1 <= number <= 50

Returns:
- str: A generated fortune cookie fortune.

Raises:
- ValueError: If the user's number is not between 1 and 50.
- TypeError: If the user input is not an integer.

### Code Example:

    from pykeafortune.fortune_cookie import get_fortune

    user_input = input("Enter an integer between 1 and 50 (inclusive): ")
    print(get_fortune(user_input))

### get_horoscope(birthday: str, birth_time: str, location: str) -> str

Returns a horoscope based on the user's birthday, birth time, and location of birth.

Parameters:
- birthday (str): The birthday in 'YYYY-MM-DD' format.
- birth_time (str): The birth time in 'HH:MM' format (24-hour clock).
- location (str): The location of birth (e.g., city, country).

Returns:
- str: A generated horoscope string.

Raises:
- ValueError: If the birthday or birth_time is not in the correct format, or if location is empty.

### Code Example:

    from pykeafortune.horoscope import get_horoscope

    my_horoscope = get_horoscope("2000-03-21", "12:34", "New York")
    print(my_horoscope)

### get_lucky_day(favorite_day: str) -> datetime.datetime

Returns a random future date that occurs on the user's favorite day of the week.

Parameters:
- favorite_day (str): The user's favorite day of the week (e.g. Monday, Tuesday)

Returns:
- datetime.date: A datetime.date object for the lucky day.

Raises:
- ValueError: If the user's favorite day is not a valid day of the week.
- TypeError: If the user input is not a string.

### Code Example:

    from pykeafortune.lucky_day import get_lucky_day

    user_input = input("Enter your favorite day of the week, unabbreviated: ")
    print(get_lucky_day(user_input))

### get_lucky_number(favorite_color: str) -> int

Returns a lucky number determined by the user's favorite color.

Parameters:
- favorite_color (str): The user's favorite color (e.g. blue, red)

Returns:
- int: An integer representing the user's lucky number

Raises:
- ValueError: If the user's favorite color does not exist in color -> number map
- TypeError: If the user input is not a string.

### Code Example:

    from pykeafortune.lucky_number import get_lucky_number

    user_input = input("Enter your favorite color: ")
    print(get_lucky_number(user_input))

## Example Python Program

See pykeafortune in action [here](https://github.com/software-students-spring2025/3-python-package-pyke-ult/blob/main/src/pykeafortune/__main__.py)!

## How to Contribute to pykeafortune

1. Clone the repository.

        git clone https://github.com/software-students-spring2025/3-python-package-pyke-ult.git

2. Set up the virtual environment and install the necessary dependencies.

        pip install pipenv
        pipenv install
        pipenv shell

3. Create a branch, implement your feature, push your branch to origin, then submit a PR!

### Building and Testing

To build pykeafortune in your clone, run

```sh
python -m build
```

To test pykeafortune (i.e. run unit tests) in your clone, run

```sh
pytest
```

## How to Run Your Project

To run your project as a Python script implemented in `__main__.py` in `src`, assuming you are in the proper virtual environment, simply run

```sh
python -m pykeafortune
```

Note: in your `__main__.py` file, below your implementation of `main()`, you will want to include

```sh
if __name__ == "__main__":
    main()
```

## Contributors:
[Matthew Cheng](https://github.com/mattchng)

[Maya Felix](https://github.com/mxf4596)

[James Hou](https://github.com/James-Hou22)

[Larry Yang](https://github.com/larryyang04)
