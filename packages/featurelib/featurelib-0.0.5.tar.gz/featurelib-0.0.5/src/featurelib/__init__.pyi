"""featurelib [`Module`].

Contains tools to separate complex functionality from a `main` class
to encourage better readability, extensibility, management and handling
of large or any code base.
"""

from .abc import feature, abstract, abstract_fmethod, requires, optimize

__all__ = ['feature', 'abstract',
           'abstract_fmethod', 'requires', 'optimize']