# app.py
from flask import Flask, request, jsonify, Response
import vocab
import db
import json
import csv
import io
from deck import Deck, DeckSchema
from word import Word
import sqlite3

def create_app(test_config=None):
    app = Flask(__name__)
    app.logger.setLevel(1)

    if test_config:
        app.config.update(test_config)
    else:
        app.config['DEBUG'] = True

    @app.teardown_appcontext
    def close_connection(exception):
        db.close_connection(exception)

    @app.route('/<language>/add_word', methods=['POST'])
    def add_word(language):
        data = request.json
        word = data.get("word")
        if not word:
            return jsonify({"error": "word is not provided"}), 400
        result = vocab.translate_and_define(word)

        jsonData = json.loads(result)
        vocab.validate_answer(jsonData)

        save_word(word, jsonData, Deck("default", language, DeckSchema.WORD))
        app.logger.debug(f"word {word} saved")

        return jsonify({"result": True}), 200

    @app.route('/words', methods=['GET'])
    def get_all_words():
        words = db.get_all_words()
        with open('vocabulary.csv', 'w', newline='') as file:
            fileWriter = csv.writer(file)
            fileWriter.writerow(['ID','Word', 'Translation', 'Definition', 'Example'])
            fileWriter.writerows(words)
            file.flush()

        bufferWriter = io.StringIO()
        csvWriter = csv.writer(bufferWriter)
        csvWriter.writerow(['ID','Word', 'Translation', 'Definition', 'Example'])
        csvWriter.writerows(words)
        bufferWriter.seek(0)
        return Response(
            bufferWriter,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=vocabulary.csv"}
        ), 200
    
    WORD_SAVE_QUERY = '''
                    INSERT INTO words (keyword, deck, language, translation, definition, example)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(keyword, deck) DO UPDATE SET
                    translation=excluded.translation,
                    definition=excluded.definition,
                    example=excluded.example     
               ;'''

    def save_word(keyword: str, data: dict, deck: Deck):
        conn = db.get_db()
        try:
            conn.cursor().execute(WORD_SAVE_QUERY,
                (keyword, 1, deck.language, data["translation"], data["definition"], data["example"]))
            conn.commit()
        except sqlite3.IntegrityError as e:
            print(e)

    return app


if __name__ == '__main__':
    app = create_app()
    db.init_db(app)
    app.run()