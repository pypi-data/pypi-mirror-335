import pytest
from devdice import MagicEightBall

def test_shake():
    '''
    Tests to make sure output is valid.
    '''
    ball = MagicEightBall()
    assert ball.shake() in ball.responses

def test_shake_no_responses():
    '''
    Tests functionality when the ball has no responses.
    '''
    ball = MagicEightBall()
    ball.responses = ()
    with pytest.raises(ValueError):
        ball.shake()

def test_shake_response_type():
    '''
    Tests to make sure the output is a string.
    '''
    ball = MagicEightBall()
    response = ball.shake()
    assert isinstance(response, str), "Magic 8-Ball response should be a string"
