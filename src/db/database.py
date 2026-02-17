import sqlite3 as sql
from pathlib import Path

# Define the database file path relative to the project root
BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "db"
DB_PATH = DB_DIR / "attendance.db"

# Ensure folder exists
DB_DIR.mkdir(parents=True, exist_ok=True)


def get_db_connection(db_path=DB_PATH):
    return sql.connect(db_path)

def init_db(db_path=DB_PATH):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registered_id (
            student_number TEXT PRIMARY KEY UNIQUE NOT NULL,
            qr_code TEXT UNIQUE NOT NULL
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

if __name__ == "__main__":
    get_db_connection()
    init_db()