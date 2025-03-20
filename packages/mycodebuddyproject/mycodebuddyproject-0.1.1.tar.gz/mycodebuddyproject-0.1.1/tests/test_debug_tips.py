import pytest
import src.mycodebuddyproject.get_debug_tips as get_tips

@pytest.mark.parametrize("error_type", ["syntax", "runtime", "logic"])
def test_debug_empty_string(error_type):
   """
   Test that the returned tip is not an empty string
   """
   result = get_tips.debug_tip(error_type)
   assert isinstance(result, str), f"Expected debug_tip({error_type}) to return a string. Instead, it returned {result}."
   assert len(result) > 0, f"Expected debug_tip({error_type}) to not be empty. Instead, it returned a string with {len(result)} characters."


@pytest.mark.parametrize("error_type", ["syntax", "runtime", "logic"])
def test_valid_error_type(error_type):
   """
   Test that the returned tip is in the right error type list
   """
   result = get_tips.debug_tip(error_type)
   assert result in get_tips.tips[error_type], f"Expected tip from {error_type}. Instead got {result}."


def test_invalid_error_type():
   """
   Test that the function handles invalid category correctly.
   """
   result = get_tips.debug_tip("invalid")
   assert result == "Unknown error type. Enter 'syntax', 'runtime', or 'logic'."


def test_tip_non_string_input():
   """
   Test that the functions handles non string inputs
   """
   result = get_tips.debug_tip(100)
   assert result == "Error: Please provide an error type as a string", f"Function should handle non string inputs"


@pytest.mark.parametrize("error_type", ["SYNTAX", "sYnTaX", "syntax", "RUNTIME", "rUntIMe", "runtime", "LOGIC", "LoGiC", "logic"])
def test_debug_case_insensitivity(error_type):
   """
   Test that the function is case insensitive
   """
   result = get_tips.debug_tip(error_type)
   assert result in get_tips.tips[error_type.lower()], f"Function does not handle {error_type} case insensitivity."