import sqlite3
from word import Word
from flask import g

DB_PATH = 'data/vocab.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
    db.execute('PRAGMA foreign_keys = ON;')
    return db

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db(app):
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def save_to_db(word: Word):
    with sqlite3.connect('vocab.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO words (keyword, deck, language, translation, definition, example)
                            VALUES (?, ?, ?, ?, ?, ?)
                            ON CONFLICT(keyword, deck) DO UPDATE SET
                            translation=excluded.translation,
                            definition=excluded.definition,
                            example=excluded.example     
                       ;''',
                   (word.key, word.deck, word.language, word.translation, word.definition, word.example))
        conn.commit()

def get_all_words():
    with sqlite3.connect('vocab.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM words")
        return cursor.fetchall()