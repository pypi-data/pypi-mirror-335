#Fortune Cookie test file
import pytest
from pykeafortune import fortune_cookie

@pytest.mark.parametrize("invalid_number", [0, -5, 51, 100]) # sets test numbers to anything out of range
def test_invalid_number(invalid_number):
    """test invalid numbers error message"""
    assert fortune_cookie.get_fortune(invalid_number) == "Invalid number. Please enter a number between 1 and 50."

def test_edge_case_big_fortune(): #tests the big fortunes to make sure numbers (like 1) maps correctly
    """test for big fortune (enters 1)"""
    fortune = fortune_cookie.get_fortune(1)
    assert fortune.startswith("Big Fortune: ")
    assert fortune.replace("Big Fortune: ", "") in fortune_cookie.big_fortune_messages

def test_edge_case_mid_fortune(): #tests the mid fortunes to make sure numbers (like 50) maps correctly
    """test for mid fortune (enters 50)"""
    fortune = fortune_cookie.get_fortune(50)
    assert fortune.startswith("Mid Fortune: ")
    assert fortune.replace("Mid Fortune: ", "") in fortune_cookie.mid_fortune_messages

def test_edge_case_small_fortune(): #tests small fortunes
    """test for mid fortune (enters 4)"""
    fortune = fortune_cookie.get_fortune(4)
    assert fortune.startswith("Small Fortune: ")
    assert fortune.replace("Small Fortune: ", "") in fortune_cookie.small_fortune_messages