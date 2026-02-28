import sqlite3 as sql
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "db"
DB_PATH = DB_DIR / "attendance.db"
DB_DIR.mkdir(parents=True, exist_ok=True)

def get_db_connection(db_path=DB_PATH):
    return sql.connect(db_path)

def init_db(db_path=DB_PATH):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_number TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            session_tag TEXT
        )
    """)
    conn.commit()
    conn.close()

def register_user(student_number, qr_hash, db_path=DB_PATH):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO registered_id (student_number, qr_code) VALUES (?, ?)",
            (student_number, qr_hash)
        )
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.close()
        return False
    conn.close()
    return True

def get_registered_user_by_qr(qr_hash, db_path=DB_PATH):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT student_number FROM registered_id WHERE qr_code = ?", (qr_hash,)
    )
    student = cursor.fetchone()
    conn.close()
    return student[0] if student else None

def remove_registered_user(student_number, db_path=DB_PATH):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM registered_id WHERE student_number = ?", (student_number,))
    conn.commit()
    conn.close()

def log_attendance_db(student_number: str, session_tag: str | None = None):
    from datetime import datetime
    conn = sql.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO attendance_logs (student_number, timestamp, session_tag)
        VALUES (?, ?, ?)
    """, (
        student_number,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        session_tag
    ))

    conn.commit()
    conn.close()


def count_attendance(session_tag: str | None = None):
    conn = sql.connect(DB_PATH)
    cursor = conn.cursor()

    if session_tag:
        cursor.execute("""
            SELECT COUNT(*) FROM attendance_logs
            WHERE session_tag = ?
        """, (session_tag,))
    else:
        cursor.execute("SELECT COUNT(*) FROM attendance_logs")

    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_logs(session_tag: str | None = None):
    conn = sql.connect(DB_PATH)
    cursor = conn.cursor()

    if session_tag:
        cursor.execute("""
            SELECT student_number, timestamp
            FROM attendance_logs
            WHERE session_tag = ?
        """, (session_tag,))
    else:
        cursor.execute("""
            SELECT student_number, timestamp
            FROM attendance_logs
        """)

    rows = cursor.fetchall()
    conn.close()
    return rows