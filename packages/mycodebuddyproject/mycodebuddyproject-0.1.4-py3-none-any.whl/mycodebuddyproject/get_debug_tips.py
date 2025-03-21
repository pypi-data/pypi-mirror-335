"""
Module: Debugging Tips

This module provides a function to return a random debugging tip based on the given error type.
Error types include 'syntax', 'runtime', and 'logic'. Each type returns a set of related tips to help debug issues.

Function:
    debug_tip(error_type): Returns a random tip related to the given error type.

Parameters:
    error_type (str): Type of error ('syntax', 'runtime', or 'logic').

Returns:
    str: A random debugging tip or an error message if the type is unsupported.
"""

import random

tips = {
   "syntax": [
      "Check for any missing colons in your code.",
      "Are all your brackets and parentheses properly closed?",
      "Check for inconsistent indentation in your code.",
      "Verify that your function definitions are correctly formatted.",
      "Ensure that your strings have matching quotes (' or \")."
   ],
   "runtime": [
      "Check if all your variables are declared before using them.",
      "Make sure list indices are within a valid range.",
      "Are you trying to divide by 0? This will cause an error.",
      "Double-check that you have the correct data types in operations.",
      "Use print statements to find where the error occurs."
   ],
   "logic": [
      "Walk through your code manually to find where the error is.",
      "Print values inside any loops you have.",
      "Make sure any arithmetic calculations are correct.",
      "Check for off-by-one errors in any loops or variables.",
      "Make sure that your data types are correctly used."
   ]
}

def debug_tip(error_type):
   """
   Returns random debugging tip based on the error type.
   """
   if not isinstance(error_type, str):
      return "Error: Please provide an error type as a string"

   error_type = error_type.lower()
   if error_type in tips:
      return random.choice(tips[error_type])
   return "Unknown error type. Enter 'syntax', 'runtime', or 'logic'."