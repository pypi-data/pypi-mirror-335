import pytest
import sys
import io
from DemoPackage.furtune_cookie import dev_fortune_cookie
from DemoPackage.generate_emoji import generate_emoji
from DemoPackage.owl_banner import gl_banner
from DemoPackage.daily_planner import daily_planner
from DemoPackage.password_strength import password_strength

# Tests of furtune_cookie *************************************************************
def test_dev_fortune_cookie_valid_category():
    """Test that valid categories return a correctly formatted string."""
    for category in ["general", "bug", "debug", "success"]:
        result = dev_fortune_cookie(category)
        assert isinstance(result, str)  # return type must be string type
        assert "🔮 Developer Fortune:" in result  # have prefix
        assert len(result.strip()) > 20  # effective return result

def test_dev_fortune_cookie_invalid_category():
    """Test that an invalid category defaults to 'general'."""
    result = dev_fortune_cookie("invalid_category")
    assert isinstance(result, str)
    assert "🔮 Developer Fortune:" in result
    assert len(result.strip()) > 20

def test_dev_fortune_cookie_empty_string():
    """Test that an empty string defaults to 'general'."""
    result = dev_fortune_cookie("")
    assert isinstance(result, str)
    assert "🔮 Developer Fortune:" in result
    assert len(result.strip()) > 20

def test_dev_fortune_cookie_none_input():
    """Test that passing None defaults to 'general'."""
    result = dev_fortune_cookie(None)  # None
    assert isinstance(result, str)
    assert "🔮 Developer Fortune:" in result
    assert len(result.strip()) > 20

# Tests of generate_emoji *************************************************************
def test_generate_emoji_valid():
    valid_emojis = ["😂", "🤣", "😆", "😁"]
    result = generate_emoji("laugh")
    assert result in valid_emojis, f"Expected one of {valid_emojis}, got {result}"

def test_generate_emoji_invalid():
    result = generate_emoji("unknown")
    assert result == "🤔", f"Expected default emoji '🤔', got {result}"

def test_generate_emoji_case_insensitive():
    valid_emojis = ["😂", "🤣", "😆", "😁"]
    result = generate_emoji("LAUGH")
    assert result in valid_emojis, f"Expected one of {valid_emojis} for case-insensitive input, got {result}"

def test_generate_emoji_output_type():
    result = generate_emoji("cry")
    assert isinstance(result, str), f"Expected output type str, got {type(result)}"

# Tests of owl_banner ****************************************************************
def capture_output(para):
    captured_output = io.StringIO()
    sys.stdout = captured_output  
    gl_banner(para)
    sys.stdout = sys.__stdout__   
    return captured_output.getvalue()

# Test1 (para=1)
def test_gl_banner_para_0_output():
    output = capture_output(1)
    assert "-- PROGRAM INITIALIZATION --" in output
    assert "PROJECT      : Project Name" in output

# Test2 (para=2)
def test_gl_banner_para_1_output():
    output = capture_output(2)
    assert "OS           :" in output
    assert "INFO         : Full-Stack Ninja" in output

# Test3 (para=3)
def test_gl_banner_para_2_no_banner():
    output = capture_output(3)
    assert "-- PROGRAM INITIALIZATION --" not in output  
    assert len(output.strip()) > 0  

# Test4 (Illegal Input )
def test_gl_banner_invalid_para_output():
    output = capture_output(999)
    assert "-- PROGRAM INITIALIZATION --" in output
    assert "VERSION      : 1.0" in output

# Tests of daily_planner *************************************************************
def test_daily_planner_valid_input():
    # Test daily_planner with valid input and check if the returned string contains the expected tasks.
    
    # expected output from user input
    user_input = ['Study for exam', '1', 'Go for a run', '2', 'done']
    expected_output = '[HIGH]'.ljust(10)
    expected_output += 'Study for exam'

    # actual result
    sys.stdin = io.StringIO('\n'.join(user_input))
    result = daily_planner('Alice')

    # assertions
    assert expected_output in result, f"Expected '{expected_output}'"
    sys.stdin = sys.__stdin__

def test_daily_planner_no_tasks():
    # Test daily_planner when no tasks are entered.

    # expected output from user input
    user_input = ['done']
    expected_output = '~~~~~Alice\'s schedule for today~~~~~'

    # actual result
    sys.stdin = io.StringIO('\n'.join(user_input))
    result = daily_planner('Alice')

    # assertions
    assert expected_output in result, f"Expected '{expected_output}'"
    assert '1. [LOW]' not in result, 'Expected no tasks in the planner'
    sys.stdin = sys.__stdin__

def test_daily_planner_invalid_priority():
    # Test daily_planner with invalid priority input.
    
    # expected output from user input
    user_input = ['Grocery shopping', '4', '1', 'done']
    expected_output = '[HIGH]'.ljust(10)
    expected_output += 'Grocery shopping'

    # actual result
    sys.stdin = io.StringIO('\n'.join(user_input))
    result = daily_planner('Alice')

    # assertions
    assert expected_output in result, f"Expected '{expected_output}'"
    sys.stdin = sys.__stdin__

# Tests of password_strength *************************************************************
def test_password_strength_strong():
    password = 'aB3$fG7@kL12'
    result = password_strength(password)
    assert result == '\tStrong password! 💪', f'Expected \'Strong password! 💪\', actual output: {result}'

def test_password_strength_moderate():
    password = 'Password123'
    result = password_strength(password)
    assert result == '\tModerate password. 🔒', f'Expected \'Moderate password. 🔒\', actual output: {result}'

def test_password_strength_weak():
    password = 'password'
    result = password_strength(password)
    assert result == '\tWeak password. 🚨', f'Expected \'Weak password. 🚨\', actual output: {result}'

def test_password_strength_empty():
    password = ''
    result = password_strength(password)
    assert result == '\tWeak password. 🚨', f'Expected \'Weak password. 🚨\', actual output: {result}'