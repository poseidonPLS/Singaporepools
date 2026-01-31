#!/usr/bin/env python3
"""
Module: chi_square.py
Version: 1.0.0
Purpose: Chi-square test for randomness of lottery numbers
"""

import numpy as np
from scipy import stats
from typing import Tuple


def chi_square_test(observed: dict, expected: float = None) -> dict:
    """
    Perform chi-square test on observed frequencies.
    
    Args:
        observed: Dict of number -> count
        expected: Expected count per number (if None, uses mean)
        
    Returns:
        Chi-square test results
    """
    counts = list(observed.values())
    
    if not counts:
        return {}
    
    arr = np.array(counts, dtype=float)
    n_categories = len(arr)
    
    # Calculate expected frequency
    if expected is None:
        expected = np.mean(arr)
    
    expected_arr = np.full(n_categories, expected)
    
    # Chi-square statistic
    chi2_stat = np.sum((arr - expected_arr) ** 2 / expected_arr)
    
    # Degrees of freedom
    df = n_categories - 1
    
    # P-value
    p_value = 1 - stats.chi2.cdf(chi2_stat, df)
    
    # Critical values
    critical_95 = stats.chi2.ppf(0.95, df)
    critical_99 = stats.chi2.ppf(0.99, df)
    
    # Contribution of each category to chi-square
    contributions = {}
    for num, count in observed.items():
        contrib = (count - expected) ** 2 / expected
        contributions[num] = round(contrib, 3)
    
    # Top contributors (potential non-random patterns)
    top_contributors = sorted(
        contributions.items(), 
        key=lambda x: -x[1]
    )[:10]
    
    return {
        "chi_square_statistic": round(chi2_stat, 4),
        "degrees_of_freedom": df,
        "p_value": round(p_value, 6),
        "critical_value_95": round(critical_95, 4),
        "critical_value_99": round(critical_99, 4),
        "is_random_95": chi2_stat < critical_95,
        "is_random_99": chi2_stat < critical_99,
        "expected_frequency": round(expected, 2),
        "contributions": contributions,
        "top_contributors": top_contributors,
        "interpretation": interpret_chi_square(p_value),
    }


def interpret_chi_square(p_value: float) -> str:
    """Interpret chi-square p-value."""
    if p_value > 0.10:
        return "No significant deviation from randomness (p > 0.10)"
    elif p_value > 0.05:
        return "Marginal deviation from randomness (0.05 < p < 0.10)"
    elif p_value > 0.01:
        return "Significant deviation from randomness (0.01 < p < 0.05)"
    else:
        return "Highly significant deviation from randomness (p < 0.01)"


def test_toto_randomness(draws: list[dict]) -> dict:
    """
    Test Toto number randomness with chi-square test.
    
    Args:
        draws: List of Toto draws
        
    Returns:
        Randomness test results
    """
    from collections import Counter
    
    # Count all main numbers
    number_counts = Counter()
    for draw in draws:
        for num in draw.get("winning_numbers", []):
            number_counts[num] += 1
    
    # Fill in zeros for numbers never drawn
    for num in range(1, 50):
        if num not in number_counts:
            number_counts[num] = 0
    
    # Expected: each number should appear (6/49) * total_draws times
    total_numbers = sum(number_counts.values())
    expected = total_numbers / 49
    
    result = chi_square_test(dict(number_counts), expected)
    result["total_draws"] = len(draws)
    result["total_numbers_drawn"] = total_numbers
    
    return result


def test_4d_digit_randomness(draws: list[dict]) -> dict:
    """
    Test 4D digit randomness per position.
    
    Args:
        draws: List of 4D draws
        
    Returns:
        Randomness test results per position
    """
    from collections import Counter
    
    positions = {
        "thousands": Counter(),
        "hundreds": Counter(),
        "tens": Counter(),
        "units": Counter(),
    }
    
    for draw in draws:
        for prize in ["first_prize", "second_prize", "third_prize"]:
            number = draw.get(prize, "")
            if len(number) == 4:
                positions["thousands"][number[0]] += 1
                positions["hundreds"][number[1]] += 1
                positions["tens"][number[2]] += 1
                positions["units"][number[3]] += 1
    
    results = {}
    for position, counts in positions.items():
        # Fill missing digits with zero
        for d in "0123456789":
            if d not in counts:
                counts[d] = 0
        
        total = sum(counts.values())
        expected = total / 10
        
        results[position] = chi_square_test(dict(counts), expected)
    
    return results


def consecutive_runs_test(numbers: list[int]) -> dict:
    """
    Wald-Wolfowitz runs test for randomness.
    
    Tests whether the sequence of numbers is random based on
    runs above and below the median.
    
    Args:
        numbers: Sequence of numbers to test
        
    Returns:
        Runs test results
    """
    if len(numbers) < 20:
        return {"error": "Need at least 20 observations"}
    
    arr = np.array(numbers)
    median = np.median(arr)
    
    # Create binary sequence: 1 if above median, 0 if below
    binary = (arr >= median).astype(int)
    
    # Count runs
    runs = 1
    for i in range(1, len(binary)):
        if binary[i] != binary[i-1]:
            runs += 1
    
    # Count n1 (above median) and n2 (below median)
    n1 = np.sum(binary)
    n2 = len(binary) - n1
    
    # Expected runs and standard deviation
    expected_runs = (2 * n1 * n2) / (n1 + n2) + 1
    std_runs = np.sqrt(
        (2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / 
        ((n1 + n2) ** 2 * (n1 + n2 - 1))
    )
    
    # Z-score
    z = (runs - expected_runs) / std_runs if std_runs > 0 else 0
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
    
    return {
        "observed_runs": runs,
        "expected_runs": round(expected_runs, 2),
        "z_score": round(z, 4),
        "p_value": round(p_value, 6),
        "is_random": abs(z) < 1.96,  # 95% confidence
        "n_above_median": int(n1),
        "n_below_median": int(n2),
    }
