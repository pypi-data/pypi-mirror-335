import pytest
from devdice import roulette

def test_invalid_input():
    '''
    Test for invalid input (<1 or >6).
    '''
    with pytest.raises(ValueError):
        roulette(0)
    with pytest.raises(ValueError):
        roulette(7)

def test_output():
    '''
    Test to valid output ("Unlucky, the end." or "Excellent, round passed.").
    '''
    for starting in range(1, 7):
        result = roulette(starting)
        assert result in ["Unlucky, the end.", "Excellent, round passed."], f"Unexpected result: {result} for starting={starting}"

def test_repeatedly():
    '''
    Test to function behavior over multiple runs (starting value = 3).
    '''
    results = [roulette(3) for _ in range(50)]

    assert "Unlucky, the end." in results, "'Unlucky, the end.' was not returned"
    assert "Excellent, round passed." in results, "'Excellent, round passed.' was not returned"
