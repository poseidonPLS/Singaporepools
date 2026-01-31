#!/usr/bin/env python3
"""
Script: database.py
Version: 1.0.0
Purpose: SQLite database handler for Singapore Pools 4D/Toto data

Usage:
    from execution.database import Database
    db = Database()
    db.insert_4d_draw(...)

Notes:
    - Stores all scraping results in SQLite for analysis
    - Supports both 4D and Toto draw formats
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional


class Database:
    """SQLite database handler for lottery data."""
    
    def __init__(self, db_path: str = ".tmp/singapore_pools.db"):
        """Initialize database connection and create tables if needed."""
        Path(db_path).parent.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # 4D draws table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS draws_4d (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draw_number TEXT UNIQUE NOT NULL,
                draw_date DATE NOT NULL,
                first_prize TEXT NOT NULL,
                second_prize TEXT NOT NULL,
                third_prize TEXT NOT NULL,
                starters TEXT NOT NULL,
                consolation TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Toto draws table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS draws_toto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draw_number TEXT UNIQUE NOT NULL,
                draw_date DATE NOT NULL,
                winning_numbers TEXT NOT NULL,
                additional_number INTEGER NOT NULL,
                prize_pool TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_4d_date ON draws_4d(draw_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_toto_date ON draws_toto(draw_date)")
        
        self.conn.commit()
    
    # =========================================================================
    # 4D OPERATIONS
    # =========================================================================
    
    def insert_4d_draw(
        self,
        draw_number: str,
        draw_date: str,
        first: str,
        second: str,
        third: str,
        starters: list[str],
        consolation: list[str]
    ) -> bool:
        """
        Insert a 4D draw result.
        
        Args:
            draw_number: Draw number (e.g., "3632")
            draw_date: Date string (YYYY-MM-DD)
            first: 1st prize (4-digit string)
            second: 2nd prize (4-digit string)
            third: 3rd prize (4-digit string)
            starters: List of 10 starter prizes
            consolation: List of 10 consolation prizes
            
        Returns:
            True if inserted, False if duplicate
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO draws_4d 
                (draw_number, draw_date, first_prize, second_prize, third_prize, starters, consolation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                draw_number,
                draw_date,
                first,
                second,
                third,
                json.dumps(starters),
                json.dumps(consolation)
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Duplicate draw
    
    def get_all_4d_draws(self) -> list[dict]:
        """Get all 4D draws ordered by date descending."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM draws_4d ORDER BY draw_date DESC
        """)
        rows = cursor.fetchall()
        return [self._row_to_4d_dict(row) for row in rows]
    
    def get_4d_draws_count(self) -> int:
        """Get total count of 4D draws in database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM draws_4d")
        return cursor.fetchone()[0]
    
    def _row_to_4d_dict(self, row) -> dict:
        """Convert a database row to a 4D draw dictionary."""
        return {
            "id": row["id"],
            "draw_number": row["draw_number"],
            "draw_date": row["draw_date"],
            "first_prize": row["first_prize"],
            "second_prize": row["second_prize"],
            "third_prize": row["third_prize"],
            "starters": json.loads(row["starters"]),
            "consolation": json.loads(row["consolation"]),
        }
    
    # =========================================================================
    # TOTO OPERATIONS
    # =========================================================================
    
    def insert_toto_draw(
        self,
        draw_number: str,
        draw_date: str,
        winning_numbers: list[int],
        additional_number: int,
        prize_pool: Optional[dict] = None
    ) -> bool:
        """
        Insert a Toto draw result.
        
        Args:
            draw_number: Draw number (e.g., "4151")
            draw_date: Date string (YYYY-MM-DD)
            winning_numbers: List of 6 winning numbers
            additional_number: The additional number
            prize_pool: Optional prize breakdown dict
            
        Returns:
            True if inserted, False if duplicate
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO draws_toto 
                (draw_number, draw_date, winning_numbers, additional_number, prize_pool)
                VALUES (?, ?, ?, ?, ?)
            """, (
                draw_number,
                draw_date,
                json.dumps(winning_numbers),
                additional_number,
                json.dumps(prize_pool) if prize_pool else None
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Duplicate draw
    
    def get_all_toto_draws(self) -> list[dict]:
        """Get all Toto draws ordered by date descending."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM draws_toto ORDER BY draw_date DESC
        """)
        rows = cursor.fetchall()
        return [self._row_to_toto_dict(row) for row in rows]
    
    def get_toto_draws_count(self) -> int:
        """Get total count of Toto draws in database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM draws_toto")
        return cursor.fetchone()[0]
    
    def _row_to_toto_dict(self, row) -> dict:
        """Convert a database row to a Toto draw dictionary."""
        return {
            "id": row["id"],
            "draw_number": row["draw_number"],
            "draw_date": row["draw_date"],
            "winning_numbers": json.loads(row["winning_numbers"]),
            "additional_number": row["additional_number"],
            "prize_pool": json.loads(row["prize_pool"]) if row["prize_pool"] else None,
        }
    
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    def close(self):
        """Close the database connection."""
        self.conn.close()
    
    # Alias methods for API
    def get_4d_draws(self):
        return self.get_all_4d_draws()
    
    def get_toto_draws(self):
        return self.get_all_toto_draws()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    # Quick test
    with Database() as db:
        print(f"4D draws: {db.get_4d_draws_count()}")
        print(f"Toto draws: {db.get_toto_draws_count()}")
