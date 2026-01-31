#!/usr/bin/env python3
"""
API Server for Singapore Pools Prediction Dashboard
Version: 1.0.0

Provides REST endpoints to serve lottery data and analysis results.

Usage:
    python execution/server.py
    
Endpoints:
    GET /api/data         - All draws (4D + Toto)
    GET /api/4d           - 4D draws only
    GET /api/toto         - Toto draws only
    GET /api/analysis/4d  - 4D statistical analysis
    GET /api/analysis/toto - Toto statistical analysis
"""

import json
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from execution.database import Database


# =============================================================================
# CONFIGURATION
# =============================================================================

PORT = 8080
HOST = "localhost"


# =============================================================================
# API HANDLER
# =============================================================================

class APIHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for API endpoints."""
    
    def __init__(self, *args, db=None, **kwargs):
        self.db = db
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        
        # API Routes
        if path == "/api/data":
            self.send_json(self.get_all_data())
        elif path == "/api/4d":
            self.send_json(self.get_4d_data())
        elif path == "/api/toto":
            self.send_json(self.get_toto_data())
        elif path == "/api/analysis/4d":
            self.send_json(self.get_4d_analysis())
        elif path == "/api/analysis/toto":
            self.send_json(self.get_toto_analysis())
        elif path == "/api/ai-prediction":
            self.send_json(self.get_ai_predictions())
        # Note: On-demand generation removed to save API tokens
        # AI predictions are auto-generated after each scheduled scrape
        elif path == "/api/health":
            self.send_json({"status": "ok", "version": "1.1.0"})
        else:
            # Serve static files from app directory
            self.serve_static()
    
    def send_json(self, data):
        """Send JSON response with CORS headers."""
        response = json.dumps(data, default=str).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(response))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response)
    
    def serve_static(self):
        """Serve static files from app directory."""
        # Rewrite path to app directory
        if self.path == "/" or self.path == "":
            self.path = "/app/index.html"
        elif not self.path.startswith("/app/"):
            self.path = "/app" + self.path
        
        try:
            super().do_GET()
        except Exception:
            self.send_error(404, "File not found")
    
    def get_all_data(self):
        """Get all lottery data."""
        with Database() as db:
            return {
                "toto": db.get_toto_draws(),
                "fourD": db.get_4d_draws(),
            }
    
    def get_4d_data(self):
        """Get 4D draws."""
        with Database() as db:
            return {"draws": db.get_4d_draws()}
    
    def get_toto_data(self):
        """Get Toto draws."""
        with Database() as db:
            return {"draws": db.get_toto_draws()}
    
    def get_4d_analysis(self):
        """Get 4D statistical analysis."""
        with Database() as db:
            draws = db.get_4d_draws()
        
        # Position frequency analysis for 4D
        position_freq = {"thousands": {}, "hundreds": {}, "tens": {}, "units": {}}
        for d in range(10):
            for pos in position_freq:
                position_freq[pos][str(d)] = 0
        
        for draw in draws:
            first = draw.get("first_prize", "")
            if len(first) == 4:
                position_freq["thousands"][first[0]] = position_freq["thousands"].get(first[0], 0) + 1
                position_freq["hundreds"][first[1]] = position_freq["hundreds"].get(first[1], 0) + 1
                position_freq["tens"][first[2]] = position_freq["tens"].get(first[2], 0) + 1
                position_freq["units"][first[3]] = position_freq["units"].get(first[3], 0) + 1
        
        return {
            "total_draws": len(draws),
            "position_frequency": position_freq,
            "date_range": {
                "start": draws[-1]["draw_date"] if draws else None,
                "end": draws[0]["draw_date"] if draws else None,
            }
        }
    
    def get_toto_analysis(self):
        """Get Toto statistical analysis."""
        with Database() as db:
            draws = db.get_toto_draws()
        
        if not draws:
            return {"error": "No data"}
        
        # Frequency analysis
        frequency = {i: 0 for i in range(1, 50)}
        for draw in draws:
            numbers = draw.get("winning_numbers", [])
            if isinstance(numbers, str):
                numbers = json.loads(numbers)
            for num in numbers:
                if 1 <= num <= 49:
                    frequency[num] += 1
        
        # Classification
        total_drawn = len(draws) * 6
        expected = total_drawn / 49
        
        classification = {}
        for num, count in frequency.items():
            deviation = (count - expected) / expected if expected > 0 else 0
            if deviation > 0.15:
                classification[num] = "hot"
            elif deviation < -0.15:
                classification[num] = "cold"
            else:
                classification[num] = "normal"
        
        hot_numbers = [n for n, c in classification.items() if c == "hot"]
        cold_numbers = [n for n, c in classification.items() if c == "cold"]
        
        # Gap analysis
        last_seen = {}
        for i, draw in enumerate(draws):
            numbers = draw.get("winning_numbers", [])
            if isinstance(numbers, str):
                numbers = json.loads(numbers)
            for num in numbers:
                if num not in last_seen:
                    last_seen[num] = i
        
        gaps = {i: last_seen.get(i, len(draws)) for i in range(1, 50)}
        overdue = sorted(gaps.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_draws": len(draws),
            "frequency": frequency,
            "classification": classification,
            "hot_numbers": sorted(hot_numbers),
            "cold_numbers": sorted(cold_numbers),
            "overdue": [{"number": n, "gap": g} for n, g in overdue],
            "expected_frequency": round(expected, 2),
            "date_range": {
                "start": draws[-1]["draw_date"] if draws else None,
                "end": draws[0]["draw_date"] if draws else None,
            }
        }
    
    def get_ai_predictions(self):
        """Get cached AI predictions from file."""
        predictions_file = Path(".tmp/ai_predictions.json")
        
        if predictions_file.exists():
            with open(predictions_file) as f:
                return json.load(f)
        
        return {
            "error": "No predictions available",
            "message": "AI predictions are generated automatically after each scheduled scrape"
        }
    
    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[API] {args[0]}")


# =============================================================================
# SERVER FACTORY
# =============================================================================

def make_handler(db):
    """Create handler class with database reference."""
    def handler(*args, **kwargs):
        return APIHandler(*args, db=db, **kwargs)
    return handler


def run_server(port=PORT, host=HOST):
    """Start the API server."""
    print(f"🚀 Starting Singapore Pools API Server...")
    print(f"   URL: http://{host}:{port}")
    print(f"   Dashboard: http://{host}:{port}/")
    print(f"   API Endpoints:")
    print(f"      GET /api/data")
    print(f"      GET /api/4d")
    print(f"      GET /api/toto")
    print(f"      GET /api/analysis/toto")
    print(f"      GET /api/analysis/4d")
    print()
    print("   Press Ctrl+C to stop")
    print()
    
    # Change to project root so static files work
    import os
    os.chdir(Path(__file__).parent.parent)
    
    with Database() as db:
        handler = make_handler(db)
        server = HTTPServer((host, port), handler)
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")
            server.shutdown()


# =============================================================================
# ENTRYPOINT
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Singapore Pools API Server")
    parser.add_argument("--port", type=int, default=PORT, help=f"Port (default: {PORT})")
    parser.add_argument("--host", default=HOST, help=f"Host (default: {HOST})")
    
    args = parser.parse_args()
    run_server(port=args.port, host=args.host)
