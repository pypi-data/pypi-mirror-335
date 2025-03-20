import pytest
import random
from procrastination_helper.list_of_excuses import get_excuse_list
from procrastination_helper.data.excusesData import sample_excuses

def test_get_excuse_list_returns_correct_number():
    """
    Verify that get_excuse_list returns exactly the number of requested excuses.
    If the requested number is greater than the number of available excuses,
    it should return all available excuses instead.
    """
    num_excuses = 3
    result = get_excuse_list(num_excuses)
    assert len(result) == num_excuses, f"Expected {num_excuses} excuses, but got {len(result)}"

def test_get_excuse_list_unique_entries():
    """
    Ensure that get_excuse_list returns a list of unique excuses.
    This test checks that there are no duplicate excuses in the returned list,
    which is important when using random sampling.
    """
    num_excuses = 5
    result = get_excuse_list(num_excuses)
    assert len(set(result)) == len(result), "Expected all unique excuses, but duplicates were found"

def test_get_excuse_list_zero_entries():
    """
    Verify that get_excuse_list returns an empty list when asked for 0 excuses.
    This test ensures that the function handles a request for zero items correctly,
    which should naturally result in an empty list without errors.
    """
    result = get_excuse_list(0)
    assert isinstance(result, list), "Expected result to be a list"
    assert len(result) == 0, "Expected no excuses, but got some"

def test_get_excuse_list_negative_numbers():
    """
    Verify that get_excuse_list handles negative inputs appropriately.
    Depending on the intended behavior, this can check for an error or an empty list.
    """
    with pytest.raises(ValueError):
        get_excuse_list(-1)
