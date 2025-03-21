import pytest
from devdice import Eliminator

def test_invalid_initialization():
    '''
    Test for initialization w/ less than 2 items
    '''
    with pytest.raises(ValueError):
        Eliminator(["a"])

    with pytest.raises(ValueError):
        Eliminator([])

def test_elimination():
    '''
    Test for proper elimination.
    '''
    e = Eliminator(["a", "b", "c"])

    eliminated = e.eliminate()
    assert eliminated in ["a", "b", "c"], f"Unexpected eliminated item: {eliminated}"

    assert len(e.items) == 2, f"Expected 2 items left, but got {len(e.items)}"

    eliminated = e.eliminate()
    assert eliminated in ["a", "b", "c"], f"Unexpected eliminated item: {eliminated}"

    assert len(e.items) == 1, f"Expected 1 item left, but got {len(e.items)}"

    eliminated = e.eliminate()
    assert eliminated in ["a", "b", "c"], f"Unexpected eliminated item: {eliminated}"

    assert len(e.items) == 0, f"Expected 0 items left, but got {len(e.items)}"

def test_no_items_left():
    '''
    Test if ValueError is raised when no items are left
    '''
    e = Eliminator(["a", "b", "c"])

    e.eliminate()
    e.eliminate()
    e.eliminate()

    with pytest.raises(ValueError):
        e.eliminate()
