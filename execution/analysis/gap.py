#!/usr/bin/env python3
"""
Module: gap.py
Version: 1.0.0
Purpose: Gap analysis - identify overdue numbers that haven't appeared recently
"""

from collections import defaultdict
from typing import Optional


def analyze_4d_gaps(draws: list[dict]) -> dict:
    """
    Analyze gaps for 4D numbers (how many draws since each digit appeared).
    
    Args:
        draws: List of 4D draws ordered by date (newest first)
        
    Returns:
        Gap analysis results for each position
    """
    position_gaps = {
        "thousands": defaultdict(lambda: None),
        "hundreds": defaultdict(lambda: None),
        "tens": defaultdict(lambda: None),
        "units": defaultdict(lambda: None),
    }
    
    # Track last appearance for each digit in each position
    for i, draw in enumerate(draws):
        for prize_type in ["first_prize", "second_prize", "third_prize"]:
            number = draw.get(prize_type, "")
            if len(number) == 4:
                positions = ["thousands", "hundreds", "tens", "units"]
                for pos_idx, pos in enumerate(positions):
                    digit = number[pos_idx]
                    if position_gaps[pos][digit] is None:
                        position_gaps[pos][digit] = i
    
    # Calculate current gaps (draws since last appearance)
    current_gaps = {}
    total_draws = len(draws)
    
    for position, digit_gaps in position_gaps.items():
        current_gaps[position] = {}
        for digit in "0123456789":
            last_seen = digit_gaps.get(digit)
            if last_seen is not None:
                current_gaps[position][digit] = last_seen
            else:
                current_gaps[position][digit] = total_draws  # Never seen
    
    # Find overdue digits (gap > expected)
    expected_gap = total_draws / 10  # Expected draws per digit
    overdue = {}
    
    for position, gaps in current_gaps.items():
        overdue[position] = {
            digit: gap 
            for digit, gap in gaps.items() 
            if gap > expected_gap * 1.5
        }
    
    return {
        "total_draws": total_draws,
        "current_gaps": current_gaps,
        "expected_gap": expected_gap,
        "overdue_digits": overdue,
    }


def analyze_toto_gaps(draws: list[dict]) -> dict:
    """
    Analyze gaps for Toto numbers (draws since each number last appeared).
    
    Args:
        draws: List of Toto draws ordered by date (newest first)
        
    Returns:
        Gap analysis results
    """
    last_appearance = {}  # Number -> draw index
    
    for i, draw in enumerate(draws):
        winning = draw.get("winning_numbers", [])
        additional = draw.get("additional_number")
        
        for num in winning:
            if num not in last_appearance:
                last_appearance[num] = i
        
        if additional and additional not in last_appearance:
            last_appearance[additional] = i
    
    total_draws = len(draws)
    
    # Calculate current gaps
    current_gaps = {}
    for num in range(1, 50):
        if num in last_appearance:
            current_gaps[num] = last_appearance[num]
        else:
            current_gaps[num] = total_draws  # Never appeared
    
    # Expected gap: Each number should appear every ~8 draws
    # (6 numbers drawn per draw, 49 possible numbers)
    expected_gap = 49 / 6
    
    # Classify as overdue (gap > 1.5x expected)
    overdue = {
        num: gap 
        for num, gap in current_gaps.items() 
        if gap > expected_gap * 1.5
    }
    
    # Sort by gap (most overdue first)
    sorted_gaps = sorted(current_gaps.items(), key=lambda x: -x[1])
    
    return {
        "total_draws": total_draws,
        "current_gaps": current_gaps,
        "expected_gap": round(expected_gap, 2),
        "overdue_numbers": sorted(overdue.keys()),
        "most_overdue": sorted_gaps[:10],
        "recently_appeared": sorted_gaps[-10:],
    }


def calculate_gap_statistics(gaps: dict) -> dict:
    """
    Calculate statistical measures for gaps.
    
    Args:
        gaps: Dictionary of number -> gap
        
    Returns:
        Statistical summary
    """
    values = list(gaps.values())
    
    if not values:
        return {}
    
    import numpy as np
    
    arr = np.array(values)
    
    return {
        "min": int(np.min(arr)),
        "max": int(np.max(arr)),
        "mean": round(float(np.mean(arr)), 2),
        "median": round(float(np.median(arr)), 2),
        "std": round(float(np.std(arr)), 2),
    }
