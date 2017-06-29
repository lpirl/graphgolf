"""
Contains base classes for tests.
"""

from unittest import TestCase
from abc import ABCMeta

class BaseTest(TestCase, metaclass=ABCMeta):
    """
    Base class for all our tests.
    """
