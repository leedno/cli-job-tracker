import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional

# Define the path to your database file
DB_FILE = Path("tracker.db")


def create_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn


def initialize_db():
    """Create the Job table if it doesn't exist."""
    conn = create_connection()
    cursor = conn.cursor()

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


def get_jobs() -> List[sqlite3.Row]:
    """Fetch all job applications from the database."""
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, company, title, source, status, date_applied 
        FROM jobs 
        ORDER BY id DESC
    """)
    jobs = cursor.fetchall()

    conn.close()
    return jobs


def get_job_by_id(job_id: int) -> Optional[sqlite3.Row]:
    """Fetch a single job by ID."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    job = cursor.fetchone()
    conn.close()
    return job


def update_job_status(job_id: int, new_status: str) -> bool:
    """Update only the status of a job."""
    conn = create_connection()
    cursor = conn.cursor()

    # Check existence
    cursor.execute("SELECT id FROM jobs WHERE id=?", (job_id,))
    if cursor.fetchone() is None:
        conn.close()
        return False

    cursor.execute("UPDATE jobs SET status = ? WHERE id = ?", (new_status, job_id))
    conn.commit()
    conn.close()
    return True


def update_job_details(
    job_id: int, company: str, title: str, source: str, status: str, notes: str
) -> bool:
    """Update all details of a job."""
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM jobs WHERE id=?", (job_id,))
    if cursor.fetchone() is None:
        conn.close()
        return False

    cursor.execute(
        """
        UPDATE jobs 
        SET company = ?, title = ?, source = ?, status = ?, notes = ?
        WHERE id = ?
    """,
        (company, title, source, status, notes, job_id),
    )

    conn.commit()
    conn.close()
    return True


def delete_job(job_id: int) -> bool:
    """Delete a job from the database."""
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM jobs WHERE id=?", (job_id,))
    if cursor.fetchone() is None:
        conn.close()
        return False

    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()
    return True


def get_job_counts() -> List[Tuple]:
    """Get count of jobs grouped by status for statistics."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status")
    counts = cursor.fetchall()
    conn.close()
    return counts


if __name__ == "__main__":
    initialize_db()
    print(f"Database initialized at {DB_FILE}.")
