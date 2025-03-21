import pytest
from procrastination_helper.customexcuses import get_custom_excuse

def test_get_custom_excuse_format():
    """Test if the custom excuse is formatted correctly."""
    task = "homework"
    excuse = get_custom_excuse(task)
    assert "homework" in excuse, f"Expected excuse to mention the task '{task}', but got: {excuse}"

def test_get_custom_excuse_randomness():
    """Test if multiple calls return different excuses."""
    task = "cleaning"
    excuses = {get_custom_excuse(task) for _ in range(10)}
    assert len(excuses) > 1, "Expected different excuses, but got the same one multiple times."

def test_get_custom_excuse_empty_task():
    """Test behavior when an empty task is provided."""
    task = ""
    excuse = get_custom_excuse(task)
    assert excuse is not None, "Expected a valid excuse even for an empty task."