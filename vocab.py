from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_TOKEN"))

def translate_and_define(word) -> str:
    response = client.chat.completions.create(
      model="gpt-4-turbo",
      response_format={ "type": "json_object" },
      messages=[
        {"role": "system", "content": "You are a English vocabulary assistant. You should help the user to retrieve the given word Russian translation, English definition and provide a short, a useful an example of usage this word and return as an output of JSON object of three fields: translation, definition, example"},
        {"role": "user", "content": f"Translate the next word: {word}"}
      ]
    )
    return response.choices[0].message.content

def validate_answer(data):
    if not isinstance(data, dict):
        raise ValueError("JSON data is not a dictionary")

    # Define required fields and their types
    required_fields = {
        "translation": str,
        "definition": int,
        "example": str
    }

    for field, field_type in required_fields.items():
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    print("answer is valid")