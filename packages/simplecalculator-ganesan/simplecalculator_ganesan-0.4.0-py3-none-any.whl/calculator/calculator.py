#!/usr/bin/env python3

"""
No Need to third party module,
Default use built-in function and condition
"""


class Calculator:
    """A simple calculator class."""

    def add(self, value_a, value_b):
        """ Adding the value of value_a and value_b """
        return value_a + value_b

    def subtract(self, value_a, value_b):
        """ Subtracting the value of value_a and value_b"""
        return value_a - value_b

    def multiply(self, value_a, value_b):
        """ Multiplying the value of value_a and value_b"""
        return value_a * value_b

    def divide(self, value_a, value_b):
        """Dividing the value of value_a and value_b"""
        if value_b == 0:
            raise ValueError("Cannot divide by zero")
        return value_a / value_b
