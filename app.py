from bot import init_bot
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def main():
    bot = init_bot()

    await bot.initialize()
    await bot.start()
    await bot.updater.start_polling()

    try:
        await asyncio.Event().wait()
    finally:
        await bot.stop()

if __name__ == '__main__':
    asyncio.run(main())