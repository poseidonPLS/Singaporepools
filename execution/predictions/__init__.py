"""
Predictions package for Singapore Pools lottery.
"""

from .generator import (
    generate_toto_numbers,
    generate_4d_number,
    generate_multiple_predictions,
    weighted_selection,
)

__all__ = [
    "generate_toto_numbers",
    "generate_4d_number",
    "generate_multiple_predictions",
    "weighted_selection",
]
