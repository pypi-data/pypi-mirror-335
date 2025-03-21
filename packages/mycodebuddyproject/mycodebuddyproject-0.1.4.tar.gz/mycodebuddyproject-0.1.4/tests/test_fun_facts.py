import random
import pytest

import src.mycodebuddyproject.fun_facts as fun_fact

facts = {
   "features": [
      "Python uses indentation (whitespace) to define code blocks instead of braces {}.",
      "Unlike many programming languages, Python doesn’t have a switch statement, but you can achieve similar functionality using dictionaries or if-else chains.",
      "Python doesn’t require explicit declaration of variable types. It’s dynamically typed, so you can assign a variable with an integer and later reassign it to a string without any issues.",
      "In Python, almost everything is an object, including functions and classes."
   ],
   "libraries": [
      "NumPy: One of the most used libraries in Python for scientific computing, providing support for large, multi-dimensional arrays and matrices.",
      "BeautifulSoup: A popular library for web scraping that allows you to extract data from HTML and XML files.",
      "Pip: Python’s package manager, 'pip,' is a playful acronym that stands for 'Pip Installs Packages.'",
      "Jupyter Notebooks: These are interactive notebooks that allow you to combine code, text, and visualizations in one document—perfect for data science and teaching."
   ],
   "trivia": [
      "Python was created by Guido van Rossum and first released in 1991!",
      "Python is named after the British comedy group Monty Python, not the snake!",
      "Python 2 was officially discontinued in 2020, with Python 3 being the main version now.",
      "Python's standard library is vast and is often described as being 'batteries included' because it comes with many built-in modules.",
      "Python has one of the largest programming communities in the world, making it easier to find help, tutorials, and libraries."
   ],
   "performance": [
       "Python can be optimized with Cython, a language that is a superset of Python and allows you to write C-like performance code that can run alongside Python.",
       "Tools like PyPy allow for Just-In-Time (JIT) compilation of Python code, which can significantly speed up performance.",
       "Python handles memory management automatically using a garbage collector, which cleans up unused objects to avoid memory leaks."
   ]
}

@pytest.mark.parametrize("category", ["features", "libraries", "trivia", "performance"])
def test_non_empty_string(category):
    """
    Test that the returned fact is not an empty string.
    """
    for _ in range(100):
        actual = fun_fact.get(category)
        assert isinstance(actual, str), f"Expected fun_fact({category}) to return a string. Instead, it returned {actual}."
        assert len(actual) > 0, f"Expected fun_fact({category}) not to be empty. Instead, it returned a string with {len(actual)} characters."


@pytest.mark.parametrize("category", ["features", "libraries", "trivia", "performance"])
def test_valid_category(category):
    """
    Test that the returned fact is from the correct category.
    """
    for _ in range(100):
        actual = fun_fact.get(category)
        assert actual in facts[category], f"Expected fact from category '{category}'. Instead, got: {actual}"


def test_invalid_category():
    """
    Test that the function handles invalid category correctly.
    """
    for _ in range(100):
        actual = fun_fact.get("invalid_category")
        assert actual == "Unknown error type. Enter 'syntax', 'runtime', or 'logic'.", \
            "The error message for invalid categories is incorrect."


@pytest.mark.parametrize("category", ["FEATURES", "features", "fEATURES", "TRIVIA", "tRiviA", "Performance", "PERFORMANCE", "libRARIES", "LIbraRies"])
def test_case_insensitivity(category):
    """
    Test that the function is case insensitive and returns facts from the correct category.
    """
    for _ in range(100):
        fact = fun_fact.get(category)

        # Assume that the facts are valid and that it is from the correct category.
        assert fact in facts[category.lower()], f"Fact1 does not belong to the '{category.lower()}' category."


def test_randomness():
    """
    Test that the function returns a variety of facts on consecutive calls.
    """
    
    # Track all facts returned during the test
    seen_facts = set()

    for _ in range(100):
        fact = fun_fact.get("features")  # Get a fact for the 'features' category
        seen_facts.add(fact)  # Add it to the set of seen facts
    
    # Assert that we have seen more than one unique fact
    assert len(seen_facts) > 1, "The function should return more than one unique fact after multiple calls."



