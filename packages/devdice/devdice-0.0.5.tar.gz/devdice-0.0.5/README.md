[![CI / CD](https://github.com/software-students-spring2025/3-python-package-four-locals/actions/workflows/build.yaml/badge.svg)](https://github.com/software-students-spring2025/3-python-package-four-locals/actions/workflows/build.yaml)

# Software Engineering, Spring 2025, Project 3.

## Description

This Python package allows developers to use fun randomizing functions to flip a coin, roll a dice, generate random colors, choose an option from a list, and much more!

## PyPI Website Link

You can find the link to our package on the PyPI website [here](https://pypi.org/project/devdice/).

## Installation

Install the `devdice` module with pip:
```
pip install devdice
```

## Importing `devdice` Functions

You can use any function in your own projects by it importing `devdice` then calling it directly:
```
from devdice import{
    Chooser
    Eliminator
    MagicEightBall
    roulette
    flip_a_coin
    roll_a_dice
    rock_paper_scissors
    random_color_generator
}

# Flip a coin 5 times
print(flip_a_coin(5)) # Possible Output: ['Heads', 'Heads', 'Heads', 'Heads', 'Tails']

# Generate two rock, paper, scissors outcomes
print(rock_paper_scissors(2)) # Possible Output: ['Scissors', 'Rock']
```

## Usage Examples

### `Eliminator` Class
```
elim = Eliminator(['Option A', 'Option B', 'Option C'])
print(elim.eliminate()) # Removes and returns a random option
```

### `Chooser` Class
```
chooser = Chooser(['Option A', 'Option B', 'Option C'])
print(chooser.pick()) # Returns a randomly selected option
```

### `MagicEightBall` Class
```
magic_eight_ball = MagicEightBall()
print(magic_eight_ball.shake()) # Returns a randomly selected Magic Eight Ball response
```

### `roulette(starting: int)`
```
print(roulette(2)) # Spins wheel with 2 of 6 winning positions 
```

### `flip_a_coin(num: int)`
```
print(flip_a_coin(5)) # Flips 5 coins
```

### `roll_a_dice(num: int)`
```
print(roll_a_dice(5)) # Rolls 5 dice
```

### `rock_paper_scissors(num: int = 1)`
```
print(rock_paper_scissors()) # Generates a rock, paper, scissors outcome
print(rock_paper_scissors(2)) # Generates list of 2 rock, paper, scissors outcomes
```

### `random_color_generator(num: int = 1)`
```
print(random_color_generator()) # Generates a hex-codes color string
print(random_color_generator(2)) # Generates list of 2 hex-codes color strings
```

### Demonstrative Python Script

The repository contains a script called `demo.py` which you can find [here](./demo.py). This script demonstrates all available functions in the `devdice` package, including details on their expected inputs and outputs.

## Contributing to DevDice's development

- The code is licensed under the [GNU General Public License](./LICENSE)
- Please use GitHub issues to submit bugs and report issues
- Feel free to contribute to the code

## Environment Setup for Contributors

### Virtual Environment Setup

1. In your python project's directory, if you have not done so already, Create a `pipenv`-managed virtual environment.

2. Enter that virtual environment: `pipenv shell`.

3. Install package dependencies: `pip install -r requirements.txt`.

4. Create a Python program file that imports `devdice` and uses it.

5. Run the program: `python3 my_program_filename.py`.

6. Exit the virtual environment: `exit`.

### Running Unit Testing

Simple example unit tests are included within the `tests` directory. To run these tests...

1. Install `pytest` into the virtual environment, e.g. `pipenv install pytest`

2. Run the tests from the main project directory: `python3 -m pytest`.

3. Tests should never fail. Any failed tests indicate that the production code is behaving differently from the behavior the tests expect.

### Instructions for setting up any environment vartiables and importing any starter data

There are no environemnt variables or starter data necessary for the system to operate correctly when run.

### Instructions for any "secret" configuration files

There are no "secret" configuration files such as `.env` or anything of that nature.

## Contributors

*Ordered alphabetically by last-name:*

1. [Edwin Chen](https://github.com/Eracks1012)
2. [Benjamin DeWeese](https://github.com/bdeweesevans)
3. [John Ma](https://github.com/j4ma)
4. [Forrest Williams](https://github.com/Zeklin)