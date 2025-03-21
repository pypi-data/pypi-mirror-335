import pytest
import src.mycodebuddyproject.get_help as help

@pytest.mark.parametrize("language", 
   ["python", "javascript", "java", "c#", "c++", "php", "ruby", "swift",
   "r", "sql", "kotlin", "typescript", "go", "rust", "scala", "dart", "perl"
])
def test_language_help_empty_string(language):
   """
   Test that the link is not an empty string
   """
   result = help.language_help(language)
   assert isinstance(result, str), f"Expected language_help({language}) to return a string. Instead, it returned {result}."
   assert len(result) > 0, f"Expected language_help({language}) to not be empty. Instead, it returned a string with {len(result)} characters."


@pytest.mark.parametrize("language", [
   "python", "javascript", "java", "c#", "c++", "php", "ruby", "swift",
   "r", "sql", "kotlin", "typescript", "go", "rust", "scala", "dart", "perl"
])
def test_valid_language_help(language):
   """
   Test that returned link is correct for a given language
   """
   result = help.language_help(language)
   assert result == help.docs[language], f"Expected the correct help link for {language}. Instead got {result}."


def test_invalid_language_help():
   """
   Test that function handles invalid languages correctly
   """
   result = help.language_help("invalid_language")
   expected = f"Help not available for invalid_language. Try one of the following: {', '.join(help.docs.keys())}"
   assert result == expected, f"Error message for an invalid language is incorrect."


def test_help_non_string_input():
   """
   Test that the functions handles non string inputs
   """
   result = help.language_help(100)
   assert result == "Error: Please provide a language name as a string.", f"Function should handle non string inputs"


@pytest.mark.parametrize("language", 
   ["python", "PYTHON", "pYtHoN", "javascript", "JAVASCRIPT", "JaVaScRipt", "java", 
   "JAVA", "jAvA", "c#", "C#", "c++", "C++", "php", "PHP", "pHp", "ruby", "RUBY", "rUbY",
   "swift", "SWIFT", "sWiFt", "r", "R", "sql", "SQL", "sQl", "kotlin", "KOTLIN", "kOtLiN",
   "typescript", "TYPESCRIPT", "tYpEsCrIpT", "go", "GO", "gO", "rust", "RUST", "rUsT",
   "scala", "SCALA", "sCaLa", "dart", "DART", "dArT", "perl", "PERL", "pErL"
])
def test_help_case_insensitivity(language):
   """
   Test that the function is case insensitive
   """
   result = help.language_help(language)
   assert result == help.docs[language.lower()], f"Function does not handle {language} case insensitivity."