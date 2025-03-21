import time
import pytest
from src.mycodebuddyproject.study_timer import StudyTimer

@pytest.fixture
def timer(monkeypatch):
    """
    Fixture to create a StudyTimer object with sleep overridden for faster tests.
    """
    # Override sleep to speed up tests
    monkeypatch.setattr(time, "sleep", lambda x: None)
    return StudyTimer()


def test_start_timer(timer, monkeypatch):
    """
    Test the start() method of the StudyTimer.
    """
    # Start the timer with 1 minute
    timer.start(1)
    assert timer.running is True, "Expected timer.running to be True after start()"
    assert timer.study_minutes == 1, "Expected study_minutes to be set to 1"
    assert timer.elapsed_time == 0, "Expected elapsed_time to be 0 immediately after starting"

    
def test_pause_resume_cancel(timer, monkeypatch):
    """
    Test the pause(), resume(), and cancel() methods of the StudyTimer.
    """
    # Start the timer with 1 minute duration
    monkeypatch.setattr("builtins.input", lambda prompt: "1")
    timer.start()
   
    # Pause the timer
    timer.pause()
    assert timer.paused is True, "Expected timer.paused to be True after pause()"
   
    # Resume the timer
    timer.resume()
    assert timer.paused is False, "Expected timer.paused to be False after resume()"
   
    # Cancel the timer
    timer.cancel()
    assert timer.running is False, "Expected timer.running to be False after cancel()"


def test_completion(timer, monkeypatch):
    """
    Test the completion of the StudyTimer after the set time period elapses.
    """
    # Capture the original sleep function.
    original_sleep = time.sleep
    # Replace time.sleep with a lambda that yields briefly for faster test execution.
    monkeypatch.setattr(time, "sleep", lambda x: original_sleep(0.001))
    monkeypatch.setattr("builtins.input", lambda prompt: "1")
    timer.start()
   
    # Force the elapsed time to reach the target (1 minute = 60 seconds)
    timer.elapsed_time = timer.study_minutes * 60
   
    # Wait (busy-poll) until timer.running becomes False or a timeout occurs.
    start_time = time.time()
    while timer.running and (time.time() - start_time) < 0.5:
        original_sleep(0.001)
   
    assert timer.running is False, "Expected timer.running to be False after completion"
    assert timer.completed is True, "Expected timer.completed to be True after reaching study time"
