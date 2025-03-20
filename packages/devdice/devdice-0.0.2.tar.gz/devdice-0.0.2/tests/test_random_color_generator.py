import pytest
from devdice import random_color_generator

def test_random_color_generator_valid():
    '''
    Tests if the output hexes are valid hexes.
    '''
    colors = random_color_generator(5)
    assert len(colors) == 5
    for color in colors:
        assert len(color) == 6
        assert all(hex_char in "0123456789abcdef" for hex_char in color)

def test_random_color_generator_valid_no_args():
    '''
    Tests to see how the function handles no arguments.
    '''
    color = random_color_generator()
    assert len(color) == 6
    assert all(hex_char in "0123456789abcdef" for hex_char in color)

def test_random_color_generator_zero():
    '''
    Tests to see if the function handles a 0 value argument.
    '''
    with pytest.raises(ValueError):
        random_color_generator(0)

def test_random_color_generator_negative():
    '''
    Tests to see if the function handles a negative argument.
    '''
    with pytest.raises(ValueError):
        random_color_generator(-3)
