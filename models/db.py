import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        password TEXT,
        role TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        case_title TEXT,
        case_date TEXT,
        description TEXT,
        summary TEXT,
        predicted_ipc TEXT,
        evidence_strength TEXT,
        legal_risk TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        complainant_name TEXT,
        description TEXT,
        fir_draft TEXT,
        ipc_suggestion TEXT,
        case_status TEXT
    )
    """)

    conn.commit()
    conn.close()