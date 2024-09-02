from enum import Enum

class Deck():
    def __init__(self, name, language, schema: Enum):
        self.name = name
        self.language = language
        self.schema = schema

class DeckSchema(Enum):
    WORD = 'WORD'
    PHRASE = 'PHRASE'
    GERMAN_VERB = 'GERMAN_VERB'

    def __str__(self):
        return self.name