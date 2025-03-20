from pykeafortune.horoscope import get_horoscope
from pykeafortune.lucky_number import generate_lucky_number, ask_color

def main():
    print("Welcome to Pykeafortune - Your Personal Fortune Teller!")
    print("-" * 50)
    
    print("\nLet's start with your lucky number!")
    color = ask_color()
    lucky_number = generate_lucky_number()
    lucky_number_string = f"{lucky_number}{lucky_number}{lucky_number}"
    print(f"Your lucky number is: {lucky_number_string}")
    
    print("\nNow, let's get your personalized horoscope!")
    try:
        birthday = input("Enter your birthday (YYYY-MM-DD): ")
        birth_time = input("Enter your birth time (HH:MM): ")
        location = input("Enter your birth location: ")
        
        horoscope = get_horoscope(birthday, birth_time, location)
        print("\nYour Horoscope:")
        print("-" * 50)
        print(horoscope)
        
    except ValueError as e:
        print(f"Error: {e}")
        print("Please make sure to enter the correct format for birthday and time.")

if __name__ == "__main__":
    main()