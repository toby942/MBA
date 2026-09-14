import sqlite3

def init_db():
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            group_msg_id INTEGER PRIMARY KEY,
            user_id INTEGER
        )
    """)
    conn.commit()
    conn.close()

def save_lead(group_msg_id, user_id):
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO leads (group_msg_id, user_id) VALUES (?, ?)", (group_msg_id, user_id))
    conn.commit()
    conn.close()

def get_user_id(group_msg_id):
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM leads WHERE group_msg_id = ?", (group_msg_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

# Fayl chaqirilganda baza ishga tushadi
init_db()