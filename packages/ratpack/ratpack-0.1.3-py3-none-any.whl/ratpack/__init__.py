"""RatPack - A humorous Python package for simulating rat infestations in your code.

This package provides tools to simulate, count, visualize, and exterminate virtual rat infestations.
"""

from .infest import infest, count_rats, exterminate, visualize_infestation

__version__ = "0.1.0"
__all__ = ["infest", "count_rats", "exterminate", "visualize_infestation"]
