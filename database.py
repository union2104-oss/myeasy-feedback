import sqlite3

DB_NAME = "feedback.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        disciplina TEXT,
        tipo TEXT,
        titolo TEXT,
        descrizione TEXT,
        priorita TEXT,
        fonte TEXT,
        stato TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_feedback(disciplina, tipo, titolo, descrizione, priorita, fonte, stato):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO feedback (disciplina, tipo, titolo, descrizione, priorita, fonte, stato)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (disciplina, tipo, titolo, descrizione, priorita, fonte, stato))

    conn.commit()
    conn.close()


def get_all_feedback():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, disciplina, tipo, titolo, descrizione, priorita, fonte, stato
        FROM feedback
    """)

    rows = cursor.fetchall()

    conn.close()
    return rows



def delete_feedback(feedback_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM feedback WHERE id = ?", (feedback_id,))

    conn.commit()
    conn.close()