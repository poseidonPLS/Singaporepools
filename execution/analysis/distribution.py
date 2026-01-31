#!/usr/bin/env python3
"""
Module: distribution.py
Version: 1.0.0
Purpose: Bell curve / Normal distribution fitting and analysis
"""

import numpy as np
from scipy import stats


def fit_normal_distribution(frequencies: dict) -> dict:
    """
    Fit a normal distribution to observed frequencies.
    
    Args:
        frequencies: Dict of number -> count
        
    Returns:
        Distribution parameters and z-scores
    """
    values = list(frequencies.values())
    
    if not values:
        return {}
    
    arr = np.array(values, dtype=float)
    
    # Fit normal distribution
    mean = np.mean(arr)
    std = np.std(arr)
    
    # Calculate z-scores for each number
    z_scores = {}
    for num, count in frequencies.items():
        if std > 0:
            z = (count - mean) / std
        else:
            z = 0
        z_scores[num] = round(z, 3)
    
    # Perform Shapiro-Wilk test for normality
    if len(arr) >= 3:
        shapiro_stat, shapiro_p = stats.shapiro(arr)
    else:
        shapiro_stat, shapiro_p = None, None
    
    # Identify outliers (|z| > 2)
    outliers = {
        num: z for num, z in z_scores.items() 
        if abs(z) > 2
    }
    
    return {
        "mean": round(mean, 2),
        "std": round(std, 2),
        "min": int(np.min(arr)),
        "max": int(np.max(arr)),
        "z_scores": z_scores,
        "outliers": outliers,
        "shapiro_test": {
            "statistic": round(shapiro_stat, 4) if shapiro_stat else None,
            "p_value": round(shapiro_p, 4) if shapiro_p else None,
            "is_normal": shapiro_p > 0.05 if shapiro_p else None,
        },
    }


def analyze_sum_distribution(draws: list[dict], game_type: str = "toto") -> dict:
    """
    Analyze the distribution of number sums.
    
    Args:
        draws: List of draw dictionaries
        game_type: 'toto' or '4d'
        
    Returns:
        Sum distribution analysis
    """
    sums = []
    
    for draw in draws:
        if game_type == "toto":
            winning = draw.get("winning_numbers", [])
            if winning:
                sums.append(sum(winning))
        else:
            for prize in ["first_prize", "second_prize", "third_prize"]:
                number = draw.get(prize, "")
                if len(number) == 4:
                    digit_sum = sum(int(d) for d in number)
                    sums.append(digit_sum)
    
    if not sums:
        return {}
    
    arr = np.array(sums)
    
    # Fit normal distribution
    mean = np.mean(arr)
    std = np.std(arr)
    
    # Create histogram bins
    hist, bin_edges = np.histogram(arr, bins=20)
    
    # Most common sum ranges
    from collections import Counter
    sum_counts = Counter(sums)
    
    return {
        "total_samples": len(sums),
        "mean_sum": round(mean, 2),
        "std_sum": round(std, 2),
        "min_sum": int(np.min(arr)),
        "max_sum": int(np.max(arr)),
        "median_sum": int(np.median(arr)),
        "most_common_sums": sum_counts.most_common(10),
        "histogram": {
            "counts": hist.tolist(),
            "bin_edges": [round(e, 1) for e in bin_edges.tolist()],
        },
        "recommended_sum_range": (
            int(mean - std),
            int(mean + std)
        ),
    }


def analyze_odd_even_distribution(draws: list[dict]) -> dict:
    """
    Analyze odd/even number distribution in Toto draws.
    
    Returns:
        Odd/even ratio analysis
    """
    from collections import Counter
    
    patterns = Counter()  # (odd_count, even_count) tuples
    
    for draw in draws:
        winning = draw.get("winning_numbers", [])
        if winning:
            odd_count = sum(1 for n in winning if n % 2 == 1)
            even_count = len(winning) - odd_count
            patterns[(odd_count, even_count)] += 1
    
    # Convert to readable format
    pattern_stats = {}
    for (odd, even), count in patterns.most_common():
        key = f"{odd}O-{even}E"
        pattern_stats[key] = {
            "count": count,
            "percentage": round(count / len(draws) * 100, 1) if draws else 0,
        }
    
    return {
        "total_draws": len(draws),
        "patterns": pattern_stats,
        "most_common_pattern": patterns.most_common(1)[0] if patterns else None,
    }


def analyze_high_low_distribution(draws: list[dict], midpoint: int = 25) -> dict:
    """
    Analyze high/low number distribution in Toto draws.
    
    Args:
        draws: List of draws
        midpoint: Number dividing low (<=) from high (>)
        
    Returns:
        High/low distribution analysis
    """
    from collections import Counter
    
    patterns = Counter()
    
    for draw in draws:
        winning = draw.get("winning_numbers", [])
        if winning:
            low_count = sum(1 for n in winning if n <= midpoint)
            high_count = len(winning) - low_count
            patterns[(low_count, high_count)] += 1
    
    pattern_stats = {}
    for (low, high), count in patterns.most_common():
        key = f"{low}L-{high}H"
        pattern_stats[key] = {
            "count": count,
            "percentage": round(count / len(draws) * 100, 1) if draws else 0,
        }
    
    return {
        "midpoint": midpoint,
        "total_draws": len(draws),
        "patterns": pattern_stats,
        "most_common_pattern": patterns.most_common(1)[0] if patterns else None,
    }
