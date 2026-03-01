import os
import sys
import sqlite3 as sql
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "db"
DB_PATH = DB_DIR / "attendance.db"
DB_DIR.mkdir(parents=True, exist_ok=True)


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        # Running as PyInstaller EXE
        base_path = sys._MEIPASS
    else:
        # Running normally
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


conn = sql.connect(resource_path(str(DB_PATH)), timeout=10)
cursor = conn.cursor()


def init_db(db_path=DB_PATH):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registered_id (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_number TEXT UNIQUE NOT NULL,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            section TEXT NOT NULL,
            subject TEXT NOT NULL,
            qr_code TEXT UNIQUE NOT NULL
        )
        """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_number TEXT NOT NULL,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            section TEXT NOT NULL,
            subject TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT UNIQUE NOT NULL
        )
        """)
    conn.commit()

def register_user(
    student_number, qr_hash, last_name, first_name, section, subject, db_path=DB_PATH
):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO registered_id (student_number, qr_code, last_name, first_name, section, subject) VALUES (?, ?, ?, ?, ?, ?)",
            (student_number, qr_hash, last_name, first_name, section, subject),
        )
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.close()
        return False
    return True


def get_registered_user_by_qr(qr_hash, db_path=DB_PATH):
    cursor.execute(
        """
        SELECT student_number, 
            last_name,
            first_name,
            section, 
            subject
        FROM registered_id
        WHERE qr_code = ?
        """,
        (qr_hash,),
    )
    student = cursor.fetchone()
    return student


def remove_registered_user(student_number, db_path=DB_PATH):
    cursor.execute(
        "DELETE FROM registered_id WHERE student_number = ?", (student_number,)
    )
    conn.commit()

def log_attendance_db(student_number, last_name, first_name, section, subject):
    from datetime import datetime
    import sqlite3 as sql

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sql.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO attendance_logs(
            student_number, 
            last_name, 
            first_name, 
            section, 
            subject, 
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (student_number, last_name, first_name, section, subject, timestamp),
    )
    conn.commit()
    return timestamp


def count_attendance(subject: str | None = None, section: str | None = None):
    query = "SELECT COUNT(*) FROM attendance_logs WHERE 1=1"
    params = []

    if subject:
        query += " AND subject = ?"
        params.append(subject)
    if section:
        query += " AND section = ?"
        params.append(section)

    cursor.execute(query, tuple(params))
    return cursor.fetchone()[0]

def get_logs(subject: str | None = None, section: str | None = None):
    query = """
        SELECT student_number, last_name, first_name, section, subject, timestamp
        FROM attendance_logs
        WHERE 1=1
    """
    params = []

    if subject:
        query += " AND subject = ?"
        params.append(subject)
    if section:
        query += " AND section = ?"
        params.append(section)

    cursor.execute(query, tuple(params))
    return cursor.fetchall()


def add_subject(subject_name):
    cursor.execute(
        """INSERT OR IGNORE INTO subjects (subject_name) VALUES (?)""", (subject_name,)
    )
    conn.commit()

def get_subjects():
    cursor.execute("SELECT subject_name FROM subjects")
    subjects = [row[0] for row in cursor.fetchall()]
    return subjects