import sqlite3
import os

db_file = 'users.db'


def add_data(username, user_id):
    if not os.path.exists(db_file):
        db = sqlite3.connect(db_file)
        curs = db.cursor()
        curs.execute("""
        CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        id_user INTEGER UNIQUE
        );
        """)
        db.commit()
    else:
        db = sqlite3.connect(db_file)
        curs = db.cursor()

    curs.execute(f"SELECT username FROM users WHERE username = ?", [username])
    # Если уже есть в БД
    if curs.fetchall():
        db.close()
    # Если нет в БД
    else:
        curs.execute("""
            INSERT INTO users(username, id_user)
            VALUES(?, ?);
            """, [username, user_id])
        db.commit()
    db.close()

