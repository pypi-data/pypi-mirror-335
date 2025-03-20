"""Program to generate a lucky number based on user input"""



import random




def ask_color():
    """function to ask for color"""
    color = input("What's your favorite color? ")
    return color.strip()




def generate_lucky_number():
    """function to generate a random number"""
    return random.randint(1, 9)





def main():
    """main"""
    ask_color()
    lucky_number = generate_lucky_number()
    #triple number
    lucky_number_string = f"{lucky_number}{lucky_number}{lucky_number}"
    print(f"Your lucky number for is: {lucky_number_string}")





if __name__ == "__main__":
    #only run in __main__ and not during tests
    main()
