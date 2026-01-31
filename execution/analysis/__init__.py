"""
Analysis package for Singapore Pools lottery prediction.
"""

from .frequency import (
    analyze_4d_frequency,
    analyze_toto_frequency,
    calculate_time_weighted_frequency,
    classify_frequency,
)
from .gap import (
    analyze_4d_gaps,
    analyze_toto_gaps,
    calculate_gap_statistics,
)
from .distribution import (
    analyze_sum_distribution,
    analyze_odd_even_distribution,
    analyze_high_low_distribution,
    fit_normal_distribution,
)
from .chi_square import (
    chi_square_test,
    test_toto_randomness,
    test_4d_digit_randomness,
    consecutive_runs_test,
)
from .patterns import (
    analyze_4d_patterns,
    analyze_toto_patterns,
    detect_repeating_patterns,
    find_number_pairs,
)

__all__ = [
    "analyze_4d_frequency",
    "analyze_toto_frequency",
    "calculate_time_weighted_frequency",
    "classify_frequency",
    "analyze_4d_gaps",
    "analyze_toto_gaps",
    "calculate_gap_statistics",
    "analyze_sum_distribution",
    "analyze_odd_even_distribution",
    "analyze_high_low_distribution",
    "fit_normal_distribution",
    "chi_square_test",
    "test_toto_randomness",
    "test_4d_digit_randomness",
    "consecutive_runs_test",
    "analyze_4d_patterns",
    "analyze_toto_patterns",
    "detect_repeating_patterns",
    "find_number_pairs",
]
