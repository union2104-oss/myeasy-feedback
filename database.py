import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
     CREATE TABLE IF NOT EXISTS feedback (
        id SERIAL PRIMARY KEY,
        project TEXT,
        disciplina TEXT,
        tipo TEXT,
        titolo TEXT,
        prompt TEXT,
        result TEXT,
        errore TEXT,
        priorita TEXT,
        fonte TEXT,
        stato TEXT,
        image_url TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback_images (
        id SERIAL PRIMARY KEY,
        feedback_id INTEGER REFERENCES feedback(id) ON DELETE CASCADE,
        image_url TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_feedback(project, disciplina, tipo, titolo, prompt, result, errore, priorita, fonte, stato, image_url):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO feedback (project, disciplina, tipo, titolo, prompt, result, errore, priorita, fonte, stato, image_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (project, disciplina, tipo, titolo, prompt, result, errore, priorita, fonte, stato, image_url))

    feedback_id = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    return feedback_id


def delete_feedback(feedback_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM feedback WHERE id = %s", (feedback_id,))

    conn.commit()
    conn.close()


def get_images_for_feedback(feedback_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT image_url
        FROM feedback_images
        WHERE feedback_id = %s
    """, (feedback_id,))

    rows = cursor.fetchall()

    conn.close()

    #ritorna lista semplice di URL
    return [row[0] for row in rows]