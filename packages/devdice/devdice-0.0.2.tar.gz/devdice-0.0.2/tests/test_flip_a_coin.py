import pytest
from devdice import flip_a_coin

def test_flip_a_coin_valid():
    '''
    Tests if the output for flip_a_coin() is valid.
    '''
    result = flip_a_coin(5)
    assert len(result) == 5
    assert all(coin in ["Heads", "Tails"] for coin in result)

def test_flip_a_coin_zero():
    '''
    Tests if the method when an argument of 0 is provided.
    '''
    with pytest.raises(ValueError):
        flip_a_coin(0)

def test_flip_a_coin_negative():
    '''
    Tests if the method when a negative argument is provided.
    '''
    with pytest.raises(ValueError):
        flip_a_coin(-3)
