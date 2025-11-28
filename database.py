import sqlite3
from pathlib import Path
from typing import List, Tuple

# Define the path to your database file
DB_FILE = Path("tracker.db")


def create_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_FILE)
    return conn


def initialize_db():
    """Create the Job table if it doesn't exist."""
    conn = create_connection()
    cursor = conn.cursor()

    # Define the table structure (Your requirements + a primary key ID)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            title TEXT NOT NULL,
            source TEXT,
            status TEXT DEFAULT 'Applied',
            notes TEXT,
            date_applied TEXT
        )
    """)
    conn.commit()
    conn.close()


# Example function to add a job (You will need to use this later)
def add_job(company: str, title: str, source: str, notes: str, date_applied: str):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO jobs (company, title, source, notes, date_applied) 
        VALUES (?, ?, ?, ?, ?)
    """,
        (company, title, source, notes, date_applied),
    )
    conn.commit()
    conn.close()


# Call the initialization when the script is imported/run
if __name__ == "__main__":
    initialize_db()
    print(f"Database initialized at {DB_FILE}. Table 'jobs' created.")
