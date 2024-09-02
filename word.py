from language import Language

class Word:
    def __init__(self, keyword, deck, language: Language, translation, definition, example):
        self.key = keyword
        self.deck = deck
        self.language = language
        self.translation = translation
        self.definition = definition
        self.example = example

    def __str__(self):
        return f"{self.key} - {self.translation} - {self.definition} - {self.example}"