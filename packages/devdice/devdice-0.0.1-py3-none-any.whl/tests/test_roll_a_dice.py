import pytest
from devdice import roll_a_dice

def test_roll_a_dice_valid():
    '''
    Rolls a dice 5 times and ensures the output is of length 5.
    '''
    result = roll_a_dice(5)
    assert len(result) == 5
    assert all(1 <= roll <= 6 for roll in result)

def test_roll_a_dice_zero():
    '''
    Tests to make sure you can not roll the dice 0 times.
    '''
    with pytest.raises(ValueError):
        roll_a_dice(0)

def test_roll_a_dice_negative():
    '''
    Tests to make sure you can not roll the dice a negative number of times.
    '''
    with pytest.raises(ValueError):
        roll_a_dice(-2)
