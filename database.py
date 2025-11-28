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


def get_jobs() -> List[Tuple]:
    """Fetch all job applications from the database."""
    conn = create_connection()
    cursor = conn.cursor()

    # Selecting the columns needed for the list view
    cursor.execute("""
        SELECT id, company, title, source, status, date_applied 
        FROM jobs 
        ORDER BY id DESC
    """)
    jobs = cursor.fetchall()

    conn.close()
    return jobs


def update_job_status(job_id: int, new_status: str):
    """Update the status of a job given its ID."""
    conn = create_connection()
    cursor = conn.cursor()

    # Check if the job exists
    cursor.execute("SELECT id FROM jobs WHERE id=?", (job_id,))
    if cursor.fetchone() is None:
        conn.close()
        return False  # Job not found

    # SQL UPDATE command
    cursor.execute(
        """
        UPDATE jobs 
        SET status = ? 
        WHERE id = ?
    """,
        (new_status, job_id),
    )

    conn.commit()
    conn.close()
    return True


# Call the initialization when the script is imported/run
if __name__ == "__main__":
    initialize_db()
    print(f"Database initialized at {DB_FILE}. Table 'jobs' created.")
