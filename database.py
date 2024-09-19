import sqlite3
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATABASE_NAME = 'bot_data.db'

def init_db():
    logger.info("Initializing database")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_data (
            chat_id BIGINT PRIMARY KEY,
            names TEXT,
            sizes TEXT
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

def write_data(chat_id, names, sizes):
    logger.info(f"Writing data for chat_id: {chat_id}")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO chat_data (chat_id, names, sizes)
        VALUES (?, ?, ?)
    ''', (chat_id, json.dumps(names), json.dumps(sizes)))
    conn.commit()
    conn.close()
    logger.info(f"Data written successfully for chat_id: {chat_id}")

def read_data(chat_id):
    logger.info(f"Reading data for chat_id: {chat_id}")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT names, sizes FROM chat_data WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        logger.info(f"Data found for chat_id: {chat_id}")
        return [str(name) for name in json.loads(result[0])], json.loads(result[1])
    logger.info(f"No data found for chat_id: {chat_id}")
    return None, None

# Initialize the database when this module is imported
def update_sizes(chat_id, sizes):
    logger.info(f"Updating sizes for chat_id: {chat_id}")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE chat_data
        SET sizes = ?
        WHERE chat_id = ?
    ''', (json.dumps(sizes), chat_id))
    conn.commit()
    conn.close()
    logger.info(f"Sizes updated successfully for chat_id: {chat_id}")