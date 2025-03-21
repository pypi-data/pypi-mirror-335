import pytest
import procrastination_helper.delay_timer as dt

# Test immediate exit (user chooses "no" right after the first cycle)
def test_delay_timer_immediate_exit(monkeypatch, capsys):
    # Override time.sleep to bypass waiting
    monkeypatch.setattr(dt.time, "sleep", lambda x: None)
    monkeypatch.setattr(dt.random, "choice", lambda x: "Fixed excuse")
    inputs = iter(["no"])
    monkeypatch.setattr("builtins.input",lambda prompt: (print(prompt, end="") or next(inputs)))

    
    dt.delay_timer(10)
    captured = capsys.readouterr().out

    assert "Procrastinating for 10 minutes..." in captured
    assert "Fixed excuse" in captured
    assert "Do you want to extend? (yes/no):" in captured
    assert "Fine, be responsible. Go do your work." in captured

# Test multiple extensions: simulate user answering "yes", "yes", then "no"
def test_delay_timer_multiple_extensions(monkeypatch, capsys):
    monkeypatch.setattr(dt.time, "sleep", lambda x: None)
    monkeypatch.setattr(dt.random, "choice", lambda x: "Fixed excuse")
    inputs = iter(["yes", "yes", "no"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
    
    dt.delay_timer(10)
    captured = capsys.readouterr().out

    # Check that multiple procrastination cycles occur.
    assert "Procrastinating for 10 minutes..." in captured
    assert captured.count("Procrastinating for 5 minutes...") >= 2
    assert captured.count("Fixed excuse") >= 3
    assert "Fine, be responsible. Go do your work." in captured

# Test edge-case where the initial minutes is 0.
def test_delay_timer_zero_initial(monkeypatch, capsys):
    monkeypatch.setattr(dt.time, "sleep", lambda x: None)
    monkeypatch.setattr(dt.random, "choice", lambda x: "Fixed excuse")
    inputs = iter(["no"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
    
    dt.delay_timer(0)
    captured = capsys.readouterr().out

    assert "Procrastinating for 0 minutes..." in captured
    assert "Fixed excuse" in captured
    assert "Fine, be responsible. Go do your work." in captured

# Test maximum extension scenario: user always answers "yes"
def test_delay_timer_max_extension(monkeypatch, capsys):
    monkeypatch.setattr(dt.time, "sleep", lambda x: None)
    monkeypatch.setattr(dt.random, "choice", lambda x: "Fixed excuse")

    inputs = iter(["yes", "yes", "yes", "yes"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
    
    dt.delay_timer(10)
    captured = capsys.readouterr().out

    # Since the user always answers "yes", the "Fine, be responsible..." message should not appear.
    assert "Fine, be responsible. Go do your work." not in captured
