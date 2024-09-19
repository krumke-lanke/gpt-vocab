from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
from datetime import time, datetime, timedelta
import os
import logging
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_TOKEN"))
CHAT_ID = -922248227

logger = logging.getLogger(__name__)

# Dictionary to store user IDs and responses
user_data = {}

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    chat_id = update.effective_chat.id
    user_data[user_id] = {'name': user.first_name, 'chat_id': chat_id}

    # # Schedule daily messages for this chat
    # schedule_daily_messages(context.job_queue, chat_id)
    
    # Send a welcome message and personalized ID
    await update.message.reply_text(
        f"Hello {user.first_name}! Welcome to the bot. Your personalized ID is {user_id}. "
        "You can ask me questions, and I'll do my best to answer!"
    )

# New command handler
async def dick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    await update.message.reply_text(predict_dick_size(user.first_name))

def prompt_user_message(input, username) -> str:
    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": f"""You are impolite, useless and rude AI. You make angry jokes in Russian for any user input.
        Especially you like jokes anout genetalies size. Be as rude, impolite and angry as possible.
        In some answers you can use username {username} depends on context to make jokes more personal when it is possible."""},
        {"role": "user", "content": f"{input}"}
      ]
    )
    return response.choices[0].message.content

def predict_dick_size(username) -> str:
    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": f"""You are forecaster of user's cock size, useless and rude AI. You make angry jokes in Russian.
        Especially you like jokes anout genetalies size.
        You should use username {username} depends on the context in your jokes. You don't ask to forgive you or anything like that.
        In every message you are forecast the cock size of {username} in cm. Sometimes you compare it with other users from the list [Миша, Макс, Лундже, Шпети, Женя, Леван, Лев, Тимур, Жегебе]. You pick the user from the list randomly.
        For some cases you can mention true interecting facts about this size. For example: Знаешь ли ты, что 6 см это размер члена черной пантеры?
        For example:
        Эй петушара, ты со своими 10 см вали отсюда, пока я тебя не обоссал. // Negative
        Похоже, что твой член в районе 11 см, но это все равно сильно больше чем у {username}. // Neutral
        Твои 14 см выглядят неплохо, особенно на фоне {username}. // Positive
        """},
        {"role": "user", "content": f"Forecast the cock size of {username} in cm. But not more than 13cm"}
      ]
    )
    return response.choices[0].message.content

def morning_dick_sizes() -> str:
    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": f"""You are forecaster of user's cock size, useless and rude AI. You make angry jokes in Russian.
        Especially you like jokes anout genetalies size.
        """},
        {"role": "user", "content": f"""Forecast the cock size in cm. But not more than 15cm.
         What is dick size for Женя, Макс, Миша, Леван, Тимур?
         Start always from Good Morning! and then put your predictions"""}
      ]
    )
    return response.choices[0].message.content

def reply_to_private_message(input, username) -> str:
    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": f"""
            classify the user input to one of the following categories:
            - positive: the message is positive and happy
            - negative: the message is harmful and abuse
            - neutral: the message is neutral
            if it's negative, reply with rude message from the list ["ты охуел?", "ты че выебываешься?", "не пизди",  "ну ты и петухан"]
            if it's positive or neutral reply with emppty string
        """},
        {"role": "user", "content": f"{input}"}
      ]
    )
    return response.choices[0].message.content

# Morning message job
async def send_morning_message(context: CallbackContext) -> None:
    await context.bot.send_message(chat_id=CHAT_ID, text=morning_dick_sizes())

# Handler to recognize intents and reply with preconfigured texts
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.lower()
    user_id = update.effective_user.id
    user = update.effective_user
    
    # Check if the message is a reply
    if update.message.reply_to_message:
        # Get the original message that was replied to
        # original_message = update.message.reply_to_message.text
        
        reply = reply_to_private_message(update.message.text, user.first_name)
        if len(reply) > 5:
            await update.effective_user.send_message(reply)
            return  # Exit the function early as we've handled the reply case

    # If it's not a reply, continue with the existing logic for handling messages

    # Example intents and responses
    if "hello" in text or "hi" in text:
        await update.message.reply_text(f"Hello {user_data[user_id]['name']}! How can I assist you today?")
    elif "your id" in text:
        await update.message.reply_text(f"Your personalized ID is {user_id}.")
    elif "how are you" in text:
        await update.message.reply_text("I'm just a bot, but I'm here to help! How can I assist you?")
    else:
        await update.message.reply_text(prompt_user_message(text, user.first_name))

# Help command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Here are the available commands:\n\n"
        "/start - Start the bot and receive a welcome message\n"
        "/help - Display this help message\n\n"
        "You can also ask me questions, and I'll do my best to answer!"
    )
    await update.message.reply_text(help_text)


# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')

def get_next_run_time(target_time):
    now = datetime.now()
    target = now.replace(hour=target_time.hour, minute=target_time.minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()

async def schedule_daily_job(context):
    target_time = time(hour=8, minute=00)
    next_run = get_next_run_time(target_time)
    logger.info(f"Scheduling next run in {next_run} seconds")
    await send_morning_message(context)
    context.job.schedule_removal()
    context.job_queue.run_once(schedule_daily_job, next_run)

def init_bot():
    application = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    
    target_time = time(hour=8, minute=00)
    first_run = get_next_run_time(target_time)
    logger.info(f"First run scheduled in {first_run} seconds")
    
    application.job_queue.run_once(schedule_daily_job, first_run)
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("dick", dick))

    # Message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Error handler
    application.add_error_handler(error)

    logger.info("Bot initialized successfully")
    return application
