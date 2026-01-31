#!/usr/bin/env python3
"""
Module: generator.py
Version: 1.0.0
Purpose: Prediction number generator using multiple strategies
"""

import random
from collections import Counter
from typing import List, Literal, Optional

import numpy as np


def generate_toto_numbers(
    strategy: Literal["random", "weighted", "hot", "cold", "overdue", "balanced"] = "weighted",
    frequency_data: Optional[dict] = None,
    gap_data: Optional[dict] = None,
    pattern_data: Optional[dict] = None,
    count: int = 6,
) -> dict:
    """
    Generate Toto number predictions using various strategies.
    
    Args:
        strategy: The prediction strategy to use
        frequency_data: Hot/cold frequency analysis results
        gap_data: Gap analysis results
        pattern_data: Pattern analysis results
        count: Number of numbers to generate (default 6 for Toto)
        
    Returns:
        Generated numbers with explanation
    """
    numbers = []
    explanation = ""
    
    if strategy == "random":
        numbers = random.sample(range(1, 50), count)
        explanation = "Purely random selection - baseline comparison"
    
    elif strategy == "hot":
        # Pick from most frequent numbers
        if frequency_data and "most_common" in frequency_data:
            hot_nums = [num for num, _ in frequency_data["most_common"][:20]]
            numbers = random.sample(hot_nums, min(count, len(hot_nums)))
            explanation = "Selected from top 20 most frequently drawn numbers"
        else:
            numbers = random.sample(range(1, 50), count)
            explanation = "Hot strategy (no data - fell back to random)"
    
    elif strategy == "cold":
        # Pick from least frequent numbers (due for appearance)
        if frequency_data and "cold_numbers" in frequency_data:
            cold_nums = frequency_data["cold_numbers"]
            if len(cold_nums) >= count:
                numbers = random.sample(cold_nums, count)
            else:
                numbers = cold_nums + random.sample(
                    [n for n in range(1, 50) if n not in cold_nums],
                    count - len(cold_nums)
                )
            explanation = "Selected from underrepresented (cold) numbers"
        else:
            numbers = random.sample(range(1, 50), count)
            explanation = "Cold strategy (no data - fell back to random)"
    
    elif strategy == "overdue":
        # Pick numbers with longest gaps since last appearance
        if gap_data and "most_overdue" in gap_data:
            overdue = [num for num, _ in gap_data["most_overdue"][:15]]
            numbers = random.sample(overdue, min(count, len(overdue)))
            explanation = "Selected from numbers with longest absence"
        else:
            numbers = random.sample(range(1, 50), count)
            explanation = "Overdue strategy (no data - fell back to random)"
    
    elif strategy == "balanced":
        # Balance between hot, cold, and random
        numbers = []
        
        # 2 hot numbers
        if frequency_data and "hot_numbers" in frequency_data:
            hot = frequency_data["hot_numbers"][:10]
            numbers.extend(random.sample(hot, min(2, len(hot))))
        
        # 2 cold/overdue numbers
        if gap_data and "overdue_numbers" in gap_data:
            cold = gap_data["overdue_numbers"][:10]
            remaining = [n for n in cold if n not in numbers]
            numbers.extend(random.sample(remaining, min(2, len(remaining))))
        
        # Fill rest with random
        while len(numbers) < count:
            candidate = random.randint(1, 49)
            if candidate not in numbers:
                numbers.append(candidate)
        
        explanation = "Balanced mix: 2 hot + 2 overdue + 2 random"
    
    elif strategy == "weighted":
        # Weighted random selection based on combined factors
        numbers = weighted_selection(
            frequency_data=frequency_data,
            gap_data=gap_data,
            count=count,
        )
        explanation = "Weighted probability combining frequency and gap analysis"
    
    return {
        "numbers": sorted(numbers),
        "strategy": strategy,
        "explanation": explanation,
    }


def weighted_selection(
    frequency_data: Optional[dict] = None,
    gap_data: Optional[dict] = None,
    count: int = 6,
    hot_weight: float = 1.5,
    gap_weight: float = 1.3,
) -> List[int]:
    """
    Select numbers using weighted probabilities.
    
    Args:
        frequency_data: Frequency analysis results
        gap_data: Gap analysis results
        count: Numbers to select
        hot_weight: Weight multiplier for hot numbers
        gap_weight: Weight multiplier for gap (overdue bonus)
        
    Returns:
        List of selected numbers
    """
    # Initialize base weights
    weights = {num: 1.0 for num in range(1, 50)}
    
    # Apply frequency weighting
    if frequency_data and "classification" in frequency_data:
        for num, classification in frequency_data["classification"].items():
            if isinstance(num, int):
                if classification == "hot":
                    weights[num] *= hot_weight
                elif classification == "cold":
                    weights[num] *= 0.7  # Slight reduction for cold
    
    # Apply gap weighting (overdue bonus)
    if gap_data and "current_gaps" in gap_data:
        expected_gap = gap_data.get("expected_gap", 8)
        for num, gap in gap_data["current_gaps"].items():
            if isinstance(num, int) and gap > expected_gap:
                # Bonus increases with overdue-ness
                overdue_factor = gap / expected_gap
                weights[num] *= (1 + (overdue_factor - 1) * 0.2)
    
    # Normalize weights to probabilities
    total_weight = sum(weights.values())
    probabilities = [weights[num] / total_weight for num in range(1, 50)]
    
    # Weighted random selection without replacement
    selected = np.random.choice(
        range(1, 50),
        size=count,
        replace=False,
        p=probabilities
    )
    
    return selected.tolist()


def generate_4d_number(
    strategy: Literal["random", "hot_position", "pattern", "weighted"] = "weighted",
    frequency_data: Optional[dict] = None,
    pattern_data: Optional[dict] = None,
) -> dict:
    """
    Generate a 4D number prediction.
    
    Args:
        strategy: Prediction strategy
        frequency_data: 4D frequency analysis
        pattern_data: 4D pattern analysis
        
    Returns:
        Generated 4D number with explanation
    """
    if strategy == "random":
        number = f"{random.randint(0, 9999):04d}"
        explanation = "Purely random 4-digit number"
    
    elif strategy == "hot_position":
        # Select hottest digit for each position
        number = ""
        
        if frequency_data and "digit_frequency" in frequency_data:
            for position in ["thousands", "hundreds", "tens", "units"]:
                pos_freq = frequency_data["digit_frequency"].get(position, {})
                if pos_freq:
                    # Pick from top 3 most frequent with some randomness
                    top_digits = sorted(pos_freq.items(), key=lambda x: -x[1])[:3]
                    digit = random.choice([d for d, _ in top_digits])
                    number += digit
                else:
                    number += str(random.randint(0, 9))
            explanation = "Each digit from top 3 hottest per position"
        else:
            number = f"{random.randint(0, 9999):04d}"
            explanation = "Hot position (no data - fell back to random)"
    
    elif strategy == "pattern":
        # Generate based on common patterns (e.g., avoid all same)
        while True:
            number = f"{random.randint(0, 9999):04d}"
            # Avoid boring patterns like 0000, 1111
            if len(set(number)) > 1:
                break
        explanation = "Pattern-based: balanced digit variety"
    
    elif strategy == "weighted":
        # Weighted selection per position
        number = ""
        
        if frequency_data and "digit_frequency" in frequency_data:
            for position in ["thousands", "hundreds", "tens", "units"]:
                pos_freq = frequency_data["digit_frequency"].get(position, {})
                
                if pos_freq:
                    digits = list(pos_freq.keys())
                    counts = list(pos_freq.values())
                    
                    # Add base weight to avoid zero probabilities
                    weights = [c + 1 for c in counts]
                    total = sum(weights)
                    probs = [w / total for w in weights]
                    
                    digit = np.random.choice(digits, p=probs)
                    number += str(digit)
                else:
                    number += str(random.randint(0, 9))
            
            explanation = "Weighted by historical position frequency"
        else:
            number = f"{random.randint(0, 9999):04d}"
            explanation = "Weighted (no data - fell back to random)"
    
    return {
        "number": number,
        "strategy": strategy,
        "explanation": explanation,
    }


def generate_multiple_predictions(
    game: Literal["toto", "4d"],
    strategies: List[str] = None,
    count_per_strategy: int = 1,
    **kwargs
) -> List[dict]:
    """
    Generate multiple predictions using different strategies.
    
    Args:
        game: 'toto' or '4d'
        strategies: List of strategies to use
        count_per_strategy: Predictions per strategy
        **kwargs: Additional arguments for generators
        
    Returns:
        List of prediction results
    """
    if game == "toto":
        if strategies is None:
            strategies = ["random", "hot", "cold", "overdue", "balanced", "weighted"]
        
        results = []
        for strategy in strategies:
            for _ in range(count_per_strategy):
                result = generate_toto_numbers(strategy=strategy, **kwargs)
                results.append(result)
        return results
    
    else:  # 4d
        if strategies is None:
            strategies = ["random", "hot_position", "pattern", "weighted"]
        
        results = []
        for strategy in strategies:
            for _ in range(count_per_strategy):
                result = generate_4d_number(strategy=strategy, **kwargs)
                results.append(result)
        return results
