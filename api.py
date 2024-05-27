from flask import Flask, request, jsonify, Response
import vocab
import db
import json
import csv
import io

app = Flask(__name__)

@app.route('/add_word', methods=['POST'])
def add_word():
    data = request.json
    word = data.get("word")
    if not word:
        return jsonify({"error": "word is not provided"}), 400
    result = vocab.translate_and_define(word)

    jsonData = json.loads(result)
    vocab.validate_answer(jsonData)

    db.save_to_db(word=word, translation=jsonData["translation"], definition=jsonData["definition"], example=jsonData["example"])
    print(f"word {word} saved")

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


if __name__ == '__main__':
    db.init_db()
    app.run()