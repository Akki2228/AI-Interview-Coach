import sqlite3

def get_db_connection():
    return sqlite3.connect("interviews.db", check_same_thread=False)

def create_table():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT,
            feedback TEXT,
            score REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()

def save_result(question, answer, feedback, score):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO results (question, answer, feedback, score)
        VALUES (?, ?, ?, ?)
        """, (question, answer, feedback, score))
        conn.commit()

def get_results():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, question, answer, feedback, score FROM results ORDER BY id DESC")
        return cursor.fetchall()