# Fortune cookie file
import random

"""Program to generate a fortune (like in fortune cookies) based on user input of a number"""

#fortune messages
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

def get_fortune(number: int) -> str:
    if not (1 <= number <= 50):
        return "Invalid number. Please enter a number between 1 and 50."
    
    if number in {1, 2, 6, 7, 8, 9, 11, 12, 16, 17, 18, 19, 22, 26, 28, 29, 32, 37, 39, 42, 47}:  # big fortune
        return f"Big Fortune: {random.choice(big_fortune_messages)}"
    
    elif number in {3, 5, 14, 20, 24, 34, 35, 43, 44, 49, 50}:  # mid fortune
        return f"Mid Fortune: {random.choice(mid_fortune_messages)}"
    
    else:  # small Fortune
        return f"Small Fortune: {random.choice(small_fortune_messages)}"

