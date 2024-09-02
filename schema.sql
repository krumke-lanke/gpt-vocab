PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS decks (
    name VARCHAR(30) PRIMARY KEY,
    language TEXT NOT NULL,
    schema TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY, 
    keyword TEXT NOT NULL,
    deck VARCHAR(30) NOT NULL,
    language TEXT NOT NULL,
    translation TEXT,
    definition TEXT,
    example TEXT,
    UNIQUE(keyword, deck),
    FOREIGN KEY(deck) REFERENCES decks(name)
);