#!/usr/bin/env python3
"""
Module: frequency.py
Version: 1.0.0
Purpose: Hot/Cold number frequency analysis for lottery data
"""

from collections import Counter
from typing import Literal

import numpy as np


def analyze_4d_frequency(draws: list[dict]) -> dict:
    """
    Analyze digit frequency for 4D draws.
    
    Args:
        draws: List of 4D draw dictionaries
        
    Returns:
        Frequency analysis results
    """
    all_numbers = []
    digit_counts = {pos: Counter() for pos in ["thousands", "hundreds", "tens", "units"]}
    
    for draw in draws:
        for prize_type in ["first_prize", "second_prize", "third_prize"]:
            number = draw.get(prize_type, "")
            if len(number) == 4:
                all_numbers.append(number)
                digit_counts["thousands"][number[0]] += 1
                digit_counts["hundreds"][number[1]] += 1
                digit_counts["tens"][number[2]] += 1
                digit_counts["units"][number[3]] += 1
        
        for number in draw.get("starters", []) + draw.get("consolation", []):
            if len(number) == 4:
                all_numbers.append(number)
                digit_counts["thousands"][number[0]] += 1
                digit_counts["hundreds"][number[1]] += 1
                digit_counts["tens"][number[2]] += 1
                digit_counts["units"][number[3]] += 1
    
    # Calculate overall frequency of each 4-digit number
    number_freq = Counter(all_numbers)
    
    # Calculate expected frequency for uniform distribution
    total_digits = sum(sum(pos.values()) for pos in digit_counts.values())
    expected_per_digit = total_digits / 40  # 4 positions * 10 digits
    
    # Classify digits as hot/cold
    classifications = {}
    for position, counts in digit_counts.items():
        pos_total = sum(counts.values())
        expected = pos_total / 10
        
        classifications[position] = {
            digit: classify_frequency(count, expected)
            for digit, count in counts.items()
        }
    
    return {
        "total_numbers": len(all_numbers),
        "unique_numbers": len(number_freq),
        "most_common": number_freq.most_common(20),
        "digit_frequency": {pos: dict(counts) for pos, counts in digit_counts.items()},
        "digit_classification": classifications,
    }


def analyze_toto_frequency(draws: list[dict]) -> dict:
    """
    Analyze number frequency for Toto draws.
    
    Args:
        draws: List of Toto draw dictionaries
        
    Returns:
        Frequency analysis results
    """
    main_numbers = Counter()
    additional_numbers = Counter()
    all_numbers = Counter()
    
    for draw in draws:
        winning = draw.get("winning_numbers", [])
        additional = draw.get("additional_number")
        
        for num in winning:
            main_numbers[num] += 1
            all_numbers[num] += 1
        
        if additional:
            additional_numbers[additional] += 1
            all_numbers[additional] += 1
    
    # Calculate expected frequency (49 possible numbers)
    total_main = sum(main_numbers.values())
    expected = total_main / 49
    
    # Classify each number
    classifications = {
        num: classify_frequency(count, expected)
        for num, count in all_numbers.items()
    }
    
    # Calculate hot/cold lists
    hot_numbers = [num for num, cls in classifications.items() if cls == "hot"]
    cold_numbers = [num for num, cls in classifications.items() if cls == "cold"]
    
    # Numbers never drawn
    all_possible = set(range(1, 50))
    never_drawn = all_possible - set(all_numbers.keys())
    
    return {
        "total_draws": len(draws),
        "main_frequency": dict(main_numbers.most_common()),
        "additional_frequency": dict(additional_numbers.most_common()),
        "combined_frequency": dict(all_numbers.most_common()),
        "classification": classifications,
        "hot_numbers": sorted(hot_numbers),
        "cold_numbers": sorted(cold_numbers),
        "never_drawn": sorted(never_drawn),
        "most_common": all_numbers.most_common(10),
        "least_common": all_numbers.most_common()[-10:] if len(all_numbers) >= 10 else [],
    }


def classify_frequency(
    count: int, 
    expected: float, 
    threshold: float = 0.2
) -> Literal["hot", "cold", "normal"]:
    """
    Classify a number based on its frequency deviation from expected.
    
    Args:
        count: Observed count
        expected: Expected count under uniform distribution
        threshold: Deviation threshold (default 20%)
        
    Returns:
        Classification: 'hot', 'cold', or 'normal'
    """
    if expected == 0:
        return "normal"
    
    deviation = (count - expected) / expected
    
    if deviation > threshold:
        return "hot"
    elif deviation < -threshold:
        return "cold"
    else:
        return "normal"


def calculate_time_weighted_frequency(
    draws: list[dict],
    decay_factor: float = 0.95
) -> dict:
    """
    Calculate time-weighted frequency (recent draws weighted more).
    
    Args:
        draws: List of draws (assumed ordered by date, newest first)
        decay_factor: Weight decay per draw (0.95 = 5% decay per draw)
        
    Returns:
        Time-weighted frequency scores
    """
    weighted_freq = Counter()
    
    for i, draw in enumerate(draws):
        weight = decay_factor ** i
        
        winning = draw.get("winning_numbers", [])
        for num in winning:
            weighted_freq[num] += weight
    
    return dict(weighted_freq.most_common())
