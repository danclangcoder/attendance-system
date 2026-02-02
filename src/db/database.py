import sqlite3 as sql

def get_db_connection(db_path='src/db/attendance.db'):
    conn = sql.connect(db_path)
    return conn

def init_db(db_path='src/db/attendance.db'):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS registered_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_number TEXT UNIQUE NOT NULL,
        sha256_hash TEXT NOT NULL
        )
    """)

def register_user(student_number, sha256_hash, db_path='src/db/attendance.db'):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO registered_users (student_number, sha256_hash) VALUES (?, ?)",
                   (student_number, sha256_hash))
    conn.commit()
    conn.close()

def get_registered_user(student_number, db_path='attendance.db'):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registered_users WHERE student_number = ?", (student_number,))
    user = cursor.fetchone()
    conn.close()
    return user

def remove_registered_user(student_number, db_path='src/db/attendance.db'):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM registered_users WHERE student_number = ?", (student_number))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    student_number = 'A123F0025'
    # hash = sha_256.create_key(student_number)
    register_user(student_number, hash)
    remove_registered_user(student_number)