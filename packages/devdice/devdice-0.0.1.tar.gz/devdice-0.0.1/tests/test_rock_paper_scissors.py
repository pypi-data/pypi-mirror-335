import pytest
from devdice import rock_paper_scissors

def test_rock_paper_scissors_valid():
    '''
    Runs 5 r-p-s simulations and tests to make sure the outcomes are valid.
    '''
    outcomes = rock_paper_scissors(5)
    assert len(outcomes) == 5
    for outcome in outcomes:
        assert outcome in ['Rock', 'Paper', 'Scissors']

def test_rock_paper_scissors_no_args():
    '''
    Runs r-p-s with no arguments.
    '''
    outcome = rock_paper_scissors()
    assert outcome in ['Rock', 'Paper', 'Scissors']

def test_rock_paper_scissors_zero():
    '''
    Runs r-p-s with argument 0.
    '''
    with pytest.raises(ValueError):
        rock_paper_scissors(0)

def test_rock_paper_scissors_negative():
    '''
    Runs r-p-s with a negative argument.
    '''
    with pytest.raises(ValueError):
        rock_paper_scissors(-3)
