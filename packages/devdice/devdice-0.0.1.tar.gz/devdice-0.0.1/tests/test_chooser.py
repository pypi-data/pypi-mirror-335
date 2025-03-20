import pytest
from devdice import Chooser

def test_pick():
    '''
    Tests if the returned choice exists within the options provided in the argument.
    '''
    options = ["apple", "banana", "orange"]
    chooser = Chooser(options)

    assert chooser.pick() in options


def test_pick_one_option():
    '''
    Tests what happens if only one option is provided to the function.
    '''
    chooser = Chooser(["onlyone"])
    assert chooser.pick() == "onlyone"


def test_add_option():
    '''
    Tests add functionality.
    '''
    chooser = Chooser(["apple", "banana"])
    chooser.add_option("cherry")

    assert "cherry" in chooser.options, "Cherry should be in options"


def test_remove_nonexistent_option():
    '''
    Tests removal on non-existant option.
    '''
    chooser = Chooser(["apple", "banana"])
    with pytest.raises(ValueError):
        chooser.remove_option("grape")


def test_empty_init():
    '''
    Tests initialization of choose class with no args.
    '''
    with pytest.raises(ValueError):
        Chooser([])
