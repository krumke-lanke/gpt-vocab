# app.py
from flask import Flask, request, jsonify
from bot import init_bot
import logging
import asyncio
from multiprocessing import Process, Event
import signal
import sys
from telegram.ext import ApplicationBuilder

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
stop_event = Event()

def signal_handler(sig, frame):
    logger.info("Shutdown signal received. Stopping bot and Flask app...")
    stop_event.set()
    sys.exit(0)

def run_bot(stop_event):
    async def bot_main():
        bot = init_bot()
        await bot.initialize()
        await bot.start()
        logger.info("Bot started successfully.")
        try:
            await bot.updater.start_polling()
            logger.info("Bot polling started.")
            while not stop_event.is_set():
                await asyncio.sleep(1)
        finally:
            await bot.updater.stop()
            await bot.stop()
            await bot.shutdown()
            logger.info("Bot stopped successfully.")

    asyncio.run(bot_main())

def run_flask():
    app.run(debug=False, use_reloader=False)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route('/<language>/add_word', methods=['POST'])
def add_word(language):
    # Your existing add_word function...
    data = request.json
    # Process the data...
    return jsonify({"result": True}), 200

@app.route('/words', methods=['GET'])
def get_all_words():
    # Your existing get_all_words function...
    # Fetch words...
    return jsonify({"words": []}), 200

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    bot_process = Process(target=run_bot, args=(stop_event,))
    flask_process = Process(target=run_flask)

    bot_process.start()
    flask_process.start()

    try:
        bot_process.join()
        flask_process.join()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")
    finally:
        stop_event.set()
        bot_process.terminate()
        flask_process.terminate()
        bot_process.join()
        flask_process.join()
        logger.info("Application shut down successfully.")