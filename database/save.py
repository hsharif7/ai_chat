from database.db import pool

def save(r, c, ci):
    with pool.connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (role, content, chat_id) VALUES (%s,%s,%s)",
            (r, c, ci)
        )
        conn.commit()
