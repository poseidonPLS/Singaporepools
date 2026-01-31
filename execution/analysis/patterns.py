#!/usr/bin/env python3
"""
Module: patterns.py
Version: 1.0.0
Purpose: Pattern recognition for lottery numbers
"""

import re
from collections import Counter
from typing import List, Tuple


def analyze_4d_patterns(draws: list[dict]) -> dict:
    """
    Analyze patterns in 4D numbers.
    
    Args:
        draws: List of 4D draws
        
    Returns:
        Pattern analysis results
    """
    patterns = {
        "all_same": 0,          # 1111, 2222
        "all_different": 0,      # 1234
        "two_pairs": 0,          # 1122
        "three_same": 0,         # 1112
        "two_same": 0,           # 1123
        "palindrome": 0,         # 1221
        "sequential": 0,         # 1234, 4321
        "double_digit": 0,       # XX00, 00XX
    }
    
    sum_distribution = Counter()
    first_last_same = 0
    
    all_numbers = []
    
    for draw in draws:
        for prize in ["first_prize", "second_prize", "third_prize"]:
            number = draw.get(prize, "")
            if len(number) == 4:
                all_numbers.append(number)
                
                # Analyze pattern
                pattern = categorize_4d_pattern(number)
                if pattern in patterns:
                    patterns[pattern] += 1
                
                # Sum of digits
                digit_sum = sum(int(d) for d in number)
                sum_distribution[digit_sum] += 1
                
                # First and last digit same
                if number[0] == number[3]:
                    first_last_same += 1
    
    total = len(all_numbers)
    
    # Convert to percentages
    pattern_percentages = {
        k: round(v / total * 100, 2) if total else 0
        for k, v in patterns.items()
    }
    
    return {
        "total_numbers": total,
        "patterns": patterns,
        "pattern_percentages": pattern_percentages,
        "sum_distribution": dict(sum_distribution.most_common()),
        "most_common_sum": sum_distribution.most_common(1)[0] if sum_distribution else None,
        "first_last_same_percentage": round(first_last_same / total * 100, 2) if total else 0,
    }


def categorize_4d_pattern(number: str) -> str:
    """Categorize a 4D number into a pattern type."""
    if len(number) != 4:
        return "invalid"
    
    digits = list(number)
    unique = len(set(digits))
    
    # All same (e.g., 1111)
    if unique == 1:
        return "all_same"
    
    # All different (e.g., 1234)
    if unique == 4:
        # Check if sequential
        sorted_digits = sorted(int(d) for d in digits)
        if sorted_digits == list(range(sorted_digits[0], sorted_digits[0] + 4)):
            return "sequential"
        return "all_different"
    
    # Count digit frequencies
    freq = Counter(digits)
    counts = sorted(freq.values(), reverse=True)
    
    # Three same (e.g., 1112)
    if counts == [3, 1]:
        return "three_same"
    
    # Two pairs (e.g., 1122)
    if counts == [2, 2]:
        return "two_pairs"
    
    # Two same (e.g., 1123)
    if counts == [2, 1, 1]:
        # Check palindrome
        if number == number[::-1]:
            return "palindrome"
        return "two_same"
    
    return "other"


def analyze_toto_patterns(draws: list[dict]) -> dict:
    """
    Analyze patterns in Toto draws.
    
    Args:
        draws: List of Toto draws
        
    Returns:
        Pattern analysis results
    """
    consecutive_counts = Counter()  # How many consecutive pairs
    decade_distribution = Counter()  # 1-9, 10-19, 20-29, etc.
    sum_distribution = Counter()
    
    for draw in draws:
        winning = draw.get("winning_numbers", [])
        if not winning:
            continue
        
        sorted_nums = sorted(winning)
        
        # Count consecutive pairs
        consecutive = 0
        for i in range(len(sorted_nums) - 1):
            if sorted_nums[i+1] - sorted_nums[i] == 1:
                consecutive += 1
        consecutive_counts[consecutive] += 1
        
        # Decade distribution
        decades = Counter(num // 10 for num in winning)
        for decade, count in decades.items():
            decade_distribution[decade] += count
        
        # Sum
        sum_distribution[sum(winning)] += 1
    
    # Analyze consecutive patterns
    has_consecutive = sum(v for k, v in consecutive_counts.items() if k > 0)
    
    return {
        "total_draws": len(draws),
        "consecutive_pair_distribution": dict(consecutive_counts),
        "draws_with_consecutive": has_consecutive,
        "consecutive_percentage": round(has_consecutive / len(draws) * 100, 2) if draws else 0,
        "decade_distribution": dict(decade_distribution.most_common()),
        "sum_distribution": dict(sum_distribution.most_common(10)),
        "average_sum": round(sum(k * v for k, v in sum_distribution.items()) / len(draws), 1) if draws else 0,
    }


def detect_repeating_patterns(draws: list[dict], window: int = 10) -> dict:
    """
    Detect if certain patterns repeat within a window.
    
    Args:
        draws: List of draws (newest first)
        window: Number of recent draws to analyze
        
    Returns:
        Repeating pattern analysis
    """
    recent_draws = draws[:window]
    
    if len(recent_draws) < 2:
        return {}
    
    # For Toto: find numbers that appeared multiple times in window
    number_appearances = Counter()
    for draw in recent_draws:
        for num in draw.get("winning_numbers", []):
            number_appearances[num] += 1
    
    # Numbers appearing more than once
    repeated = {
        num: count 
        for num, count in number_appearances.items() 
        if count > 1
    }
    
    return {
        "window_size": window,
        "repeated_numbers": repeated,
        "most_repeated": number_appearances.most_common(5),
    }


def find_number_pairs(draws: list[dict], min_occurrences: int = 5) -> dict:
    """
    Find frequently co-occurring number pairs.
    
    Args:
        draws: List of Toto draws
        min_occurrences: Minimum times a pair must appear
        
    Returns:
        Pair frequency analysis
    """
    pair_counts = Counter()
    
    for draw in draws:
        winning = draw.get("winning_numbers", [])
        if len(winning) < 2:
            continue
        
        # Generate all pairs
        for i in range(len(winning)):
            for j in range(i + 1, len(winning)):
                pair = tuple(sorted([winning[i], winning[j]]))
                pair_counts[pair] += 1
    
    # Filter by minimum occurrences
    frequent_pairs = {
        pair: count 
        for pair, count in pair_counts.items() 
        if count >= min_occurrences
    }
    
    return {
        "total_pairs_found": len(pair_counts),
        "pairs_above_threshold": len(frequent_pairs),
        "threshold": min_occurrences,
        "most_common_pairs": pair_counts.most_common(20),
    }
