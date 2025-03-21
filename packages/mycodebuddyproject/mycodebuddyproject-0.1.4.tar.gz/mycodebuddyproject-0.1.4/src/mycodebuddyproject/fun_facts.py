"""
Module: Python Fun Facts

This module provides a function to return a random Python-related fun fact based on the given fact type.
Fact types include 'features', 'libraries', 'trivia', and 'performance'. Each type returns a set of related fun facts.

Function:
    get(fact_type): Returns a random Python fun fact related to the specified type.

Parameters:
    fact_type (str): Type of fun fact ('features', 'libraries', 'trivia', 'performance').

Returns:
    str: A random Python fun fact or an error message if the type is unsupported.
"""

import random

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
def get(fact_type):
   """
   Returns random Python related fun facts based on the fact type.
   """
   fact_type = fact_type.lower()

   if fact_type in facts:
      return random.choice(facts[fact_type])
   return "Unknown error type. Enter 'syntax', 'runtime', or 'logic'."