import sqlite3

# Set up the database
def init_db():
    with sqlite3.connect('vocab.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS vocab
                      (id INTEGER PRIMARY KEY, word TEXT UNIQUE, translation TEXT, definition TEXT, example TEXT)''')
        conn.commit()

def save_to_db(word, translation, definition, example):
    with sqlite3.connect('vocab.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO vocab (word, translation, definition, example)
                                VALUES (?, ?, ?, ?)
                                ON CONFLICT(word) DO UPDATE SET
                                translation=excluded.translation,
                                definition=excluded.definition,
                                example=excluded.example     
                       ''',
                   (word, translation, definition, example))
        conn.commit()

def get_all_words():
    with sqlite3.connect('vocab.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vocab")
        return cursor.fetchall()