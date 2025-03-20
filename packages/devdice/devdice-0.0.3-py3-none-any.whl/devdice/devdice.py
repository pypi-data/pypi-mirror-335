"""
This module defines all DevDice functions.
Authors: Edwin Chen, Benjamin DeWeese, John Ma, Forrest Williams
Date: March 19, 2025
"""
import random

class Eliminator:
    """
    This is a class for an Elimination function.
    """
    def __init__(self, items):
        if len(items) < 2:
            raise ValueError("Must have at least two items.")
        self.items = list(items)

    def eliminate(self):
        """
        Pass in items as an array.
        Returns the eliminated item.
        """
        if not self.items:
            raise ValueError("No more items to eliminate!")
        return self.items.pop(random.randint(0, len(self.items) - 1))
    def get_items(self):
        """
        Returns items still in Eliminator's Storage
        """
        return self.items

class Chooser:
    """
    This is a class for a Chooser function.
    """
    def __init__(self, options):
        if not options:
            raise ValueError("Must have at least one option.")
        self.options = list(options)

    def pick(self):
        """
        Return a Random Choice
        """
        return random.choice(self.options)

    def add_option(self, option):
        """
        Add Option to Options Array
        """
        self.options.append(option)

    def remove_option(self, option):
        """
        Remove Option from Options Array
        """
        if option in self.options:
            self.options.remove(option)
        else:
            raise ValueError("Option not found.")

class MagicEightBall:
    """
    This is a class for a Magic EightBall function.
    """
    def __init__(self):
        self.responses = ["Yes, definitely!","For sure!", "100%", "I'd bet my life on it",
                           "Yessir!", "Without a doubt.", "No!", "Definitely Not!","Nahh!",
                           "No shot", "Not a chance.", "Absolutely not.",
                           "I don't think you want to know", "Maybe", "Potentially...",
                           "Could be",  "Most likely.", "Don't count on it.", "Very doubtful.",
                            "Prob", "Prob Not", "I think ur cooked", "That's Unfortunate"]
    def shake(self) -> str:
        """
        Returns Random Option From Response Array
        """
        if not self.responses:
            raise ValueError("No responses in Magic 8-Ball.")
        index = random.randint(0, len(self.responses)-1)
        return self.responses[index]

    def start_simulation(self):
        """
        Starts a Magic Ball Simulation
        """
        print("Welcome to the Magic 8 Ball! Type your question and press Enter.")
        print("Type 'exit' to quit.\n")
        while True:
            question = input("Enter your question: ").strip()
            if question.lower() == "exit":
                print("Goodbye! ")
                break
            if question == "":
                print("Please enter a valid question.")
            else:
                print(self.shake())
                print("\n")

def roulette(starting: int):
    """
    Runs an alternative roulette simulation.
    Input is the starting number of valid positions.
    Returns result of spinning the roulette wheel & landing on a positon as a string.
    """
    if starting < 1 or starting > 6:
        raise ValueError("Starting number must be between 1 and 6.")
    rand_num = random.randint(1, 6)
    if rand_num <= starting:
        return "Unlucky, the end."
    return "Excellent, round passed."

def flip_a_coin(num: int) -> list[str]:
    """
    Flips a coin an arg number of times.
    Input is the number of times to flip the coin.
    Returns the flip results as a list.
    """
    if num <= 0:
        raise ValueError("Number of flips must be greater than zero.")
    return [random.choice(["Heads", "Tails"]) for _ in range(num)]

def roll_a_dice(num: int) -> list[int]:
    """
    Rolls a 6 sided dice an arg number of times.
    Input is the number of times to roll the dice.
    Returns the roll results as a list.
    """
    if num <= 0:
        raise ValueError("Number of rolls must be greater than zero.")
    return [random.randint(1, 6) for _ in range(num)]

def rock_paper_scissors(num: int = 1) -> list[str]:
    """
    Provides random rock, paper, scissors outcome
    Input is number of outcomes requested
    Returns the rock, paper, scissors outcome(s) as a list (string if num=1)
    """
    if num <= 0:
        raise ValueError("Must request at least one RPS outcome.")
    outcomes = ['Rock', 'Paper', 'Scissors']
    if num == 1:
        return outcomes[random.randint(0, 2)]
    return [outcomes[random.randint(0, 2)] for _ in range(num)]

def random_color_generator(num: int = 1) -> list[str]:
    """
    Generates a random hexcode color
    Input is number of colors generated
    Returns generated color hexcode(s) as a list (string if num=1)
    """
    if num <= 0:
        raise ValueError("Must generate at least one color.")
    def color_gen():
        hex_color = ''
        for _ in range(6):
            hex_color += f"{random.randrange(0, 16):x}"
        return hex_color
    if num == 1:
        return color_gen()
    return [color_gen() for _ in range(num)]
