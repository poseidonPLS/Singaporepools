#!/usr/bin/env python3
"""
Script: ai_predictor.py
Version: 1.0.0
Purpose: Generate AI-powered lottery predictions using Gemini Flash 3.0

Uses historical data patterns to generate predictions via Google's Gemini API.
Runs after the scheduler fetches new data.

Usage:
    python3 execution/ai_predictor.py --game toto
    python3 execution/ai_predictor.py --game 4d
    
Environment:
    GOOGLE_API_KEY: Your Gemini API key
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required, can use env vars directly

try:
    import google.generativeai as genai
except ImportError:
    print("❌ Please install google-generativeai: pip install google-generativeai")
    sys.exit(1)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from execution.database import Database

# =============================================================================
# CONFIGURATION
# =============================================================================

MODEL_NAME = "gemini-2.0-flash"
PREDICTIONS_FILE = ".tmp/ai_predictions.json"


# =============================================================================
# AI PREDICTION ENGINE
# =============================================================================

def get_api_key() -> str:
    """Get Gemini API key from environment."""
    key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError(
            "Missing API key. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable."
        )
    return key


def prepare_toto_context(draws: list[dict], limit: int = 50) -> str:
    """Prepare Toto historical data for the AI prompt."""
    recent = draws[:limit]
    
    lines = ["Recent Toto Draw History (newest first):"]
    lines.append("Draw# | Date | Winning Numbers | Additional")
    lines.append("-" * 60)
    
    for draw in recent:
        nums = draw.get("winning_numbers", [])
        if isinstance(nums, str):
            nums = json.loads(nums)
        nums_str = ", ".join(str(n) for n in sorted(nums))
        add = draw.get("additional_number", "?")
        lines.append(f"{draw['draw_number']} | {draw['draw_date']} | {nums_str} | {add}")
    
    return "\n".join(lines)


def prepare_4d_context(draws: list[dict], limit: int = 50) -> str:
    """Prepare 4D historical data for the AI prompt."""
    recent = draws[:limit]
    
    lines = ["Recent 4D Draw History (newest first):"]
    lines.append("Draw# | Date | 1st | 2nd | 3rd")
    lines.append("-" * 50)
    
    for draw in recent:
        lines.append(
            f"{draw['draw_number']} | {draw['draw_date']} | "
            f"{draw['first_prize']} | {draw['second_prize']} | {draw['third_prize']}"
        )
    
    return "\n".join(lines)


def generate_toto_prediction(draws: list[dict]) -> dict:
    """Generate AI prediction for Toto - 4 sets with weighted confidence."""
    genai.configure(api_key=get_api_key())
    model = genai.GenerativeModel(MODEL_NAME)
    
    context = prepare_toto_context(draws)
    
    prompt = f"""You are an expert lottery analyst. Analyze the following Singapore Toto historical data and provide number predictions.

{context}

Based on pattern analysis of the above data, provide 4 DIFFERENT sets of predicted numbers, each with its own confidence level:

1. HIGH confidence set - based on strongest patterns (hot numbers, consistent frequency)
2. MEDIUM confidence set - balanced approach mixing hot and overdue numbers  
3. LOW confidence set - focusing on cold/overdue numbers due for reversion
4. SPECULATIVE set - unconventional picks based on subtle patterns

IMPORTANT: 
- Each set must have 6 unique main numbers (1-49) and 1 additional number
- All 4 sets should be DIFFERENT from each other
- Numbers must be between 1 and 49
- Consider frequency, gaps, hot/cold patterns, consecutive patterns
- This is for entertainment only

Respond in this exact JSON format:
{{
    "predictions": [
        {{
            "main_numbers": [n1, n2, n3, n4, n5, n6],
            "additional_number": n,
            "confidence": "high",
            "reasoning": "Brief explanation"
        }},
        {{
            "main_numbers": [n1, n2, n3, n4, n5, n6],
            "additional_number": n,
            "confidence": "medium",
            "reasoning": "Brief explanation"
        }},
        {{
            "main_numbers": [n1, n2, n3, n4, n5, n6],
            "additional_number": n,
            "confidence": "low",
            "reasoning": "Brief explanation"
        }},
        {{
            "main_numbers": [n1, n2, n3, n4, n5, n6],
            "additional_number": n,
            "confidence": "speculative",
            "reasoning": "Brief explanation"
        }}
    ],
    "analysis_summary": "Overall pattern analysis"
}}

Only respond with the JSON, no other text."""

    response = model.generate_content(prompt)
    
    # Parse response
    try:
        # Extract JSON from response
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        
        result = json.loads(text)
        result["generated_at"] = datetime.now().isoformat()
        result["model"] = MODEL_NAME
        result["game"] = "toto"
        return result
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse AI response",
            "raw_response": response.text[:500],
            "generated_at": datetime.now().isoformat(),
        }


def generate_4d_prediction(draws: list[dict]) -> dict:
    """Generate AI prediction for 4D - 4 sets with weighted confidence."""
    genai.configure(api_key=get_api_key())
    model = genai.GenerativeModel(MODEL_NAME)
    
    context = prepare_4d_context(draws)
    
    prompt = f"""You are an expert lottery analyst. Analyze the following Singapore 4D historical data and provide number predictions.

{context}

Based on pattern analysis of the above data, provide 4 DIFFERENT sets of predicted 4-digit numbers, each with its own confidence level:

1. HIGH confidence set - based on strongest patterns (repeating numbers, frequent digit combinations)
2. MEDIUM confidence set - balanced approach mixing hot digits with position patterns
3. LOW confidence set - focusing on cold/underrepresented digit combinations
4. SPECULATIVE set - unconventional picks based on subtle patterns or sequences

IMPORTANT:
- Each prediction must be exactly 4 digits (0000-9999)
- All 4 predictions should be DIFFERENT from each other
- Analyze digit position frequency, pairs, patterns
- This is for entertainment only

Respond in this exact JSON format:
{{
    "predictions": [
        {{
            "number": "XXXX",
            "confidence": "high",
            "reasoning": "Brief explanation"
        }},
        {{
            "number": "XXXX",
            "confidence": "medium",
            "reasoning": "Brief explanation"
        }},
        {{
            "number": "XXXX",
            "confidence": "low",
            "reasoning": "Brief explanation"
        }},
        {{
            "number": "XXXX",
            "confidence": "speculative",
            "reasoning": "Brief explanation"
        }}
    ],
    "analysis_summary": "Overall pattern analysis"
}}

Only respond with the JSON, no other text."""

    response = model.generate_content(prompt)
    
    try:
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        
        result = json.loads(text)
        result["generated_at"] = datetime.now().isoformat()
        result["model"] = MODEL_NAME
        result["game"] = "4d"
        return result
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse AI response",
            "raw_response": response.text[:500],
            "generated_at": datetime.now().isoformat(),
        }


def save_prediction(prediction: dict, game: str):
    """Save prediction to JSON file."""
    Path(".tmp").mkdir(exist_ok=True)
    
    # Load existing predictions
    predictions = {}
    if Path(PREDICTIONS_FILE).exists():
        with open(PREDICTIONS_FILE) as f:
            predictions = json.load(f)
    
    # Update with new prediction
    predictions[game] = prediction
    predictions["last_updated"] = datetime.now().isoformat()
    
    with open(PREDICTIONS_FILE, "w") as f:
        json.dump(predictions, f, indent=2)
    
    print(f"   Saved to {PREDICTIONS_FILE}")


def generate_prediction(game: str) -> dict:
    """Generate and save AI prediction for specified game."""
    print(f"🤖 Generating AI prediction for {game.upper()}...")
    
    with Database() as db:
        if game == "toto":
            draws = db.get_toto_draws()
            prediction = generate_toto_prediction(draws)
        else:
            draws = db.get_4d_draws()
            prediction = generate_4d_prediction(draws)
    
    if "error" not in prediction:
        print(f"   ✅ Prediction generated!")
        if game == "toto":
            for p in prediction.get("predictions", []):
                print(f"   {p.get('confidence', 'unknown').upper()}: {p.get('main_numbers', [])} + {p.get('additional_number')}")
        else:
            for p in prediction.get("predictions", []):
                print(f"   {p.get('confidence', 'unknown').upper()}: {p.get('number')}")
                
    else:
        print(f"   ⚠ Error: {prediction.get('error')}")
    
    save_prediction(prediction, game)
    return prediction


# =============================================================================
# ENTRYPOINT
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate AI lottery predictions")
    parser.add_argument("--game", choices=["toto", "4d", "both"], default="both",
                        help="Which game to predict")
    
    args = parser.parse_args()
    
    if args.game in ["toto", "both"]:
        generate_prediction("toto")
    
    if args.game in ["4d", "both"]:
        generate_prediction("4d")
    
    print("\n✨ AI predictions complete!")
