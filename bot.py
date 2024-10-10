from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
from datetime import time, datetime, timedelta
import os
import logging
from openai import OpenAI
from database import init_db,write_data, read_data, update_sizes
import random

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

    # Initialize or update the database entry for this chat
    names, sizes = read_data(chat_id)
    if names is None:
        names = [user.first_name]
        sizes = {user.first_name: random.randint(7, 12)}
    elif user.first_name not in names:
        names.append(user.first_name)
        sizes[user.first_name] = random.randint(7, 12)  # Initialize with 0 or any default value
    write_data(chat_id, names, sizes)

    # # Schedule daily messages for this chat
    # schedule_daily_messages(context.job_queue, chat_id)
    
    # Send a welcome message and personalized ID
    await update.message.reply_text(
        f"Hello {update.effective_chat.full_name}! Welcome to the bot. Your personalized ID is {chat_id}. "
        "You can ask me questions, and I'll do my best to answer!"
    )

# New command handler
async def dick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat_id = update.effective_chat.id

    # Read current data
    names, sizes = read_data(chat_id)
    if sizes is None:
        names = [user.first_name]
        sizes = [0]

    if user.first_name in sizes:
        await update.message.reply_text(analyze_dick(user.first_name, sizes[user.first_name], sizes))
    else:
        new_size = random.randint(7, 12)
        sizes[user.first_name] = new_size
        write_data(chat_id, names, sizes)
        await update.message.reply_text(analyze_dick(user.first_name, sizes[user.first_name], sizes))

async def dicks_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    _, sizes = read_data(chat_id)
    if sizes:
        await update.message.reply_text(morning_dick_sizes(sizes))
    else:
        await update.message.reply_text("No dicks in this chat.")

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

def predict_dick_size(username, names) -> str:
    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": f"""You are forecaster of user's cock size, useless and rude AI. You make angry jokes in Russian.
        Especially you like jokes anout genetalies size.
        You should use username {username} depends on the context in your jokes. You don't ask to forgive you or anything like that.
        In every message you are forecast the cock size of {username} in cm. Sometimes you compare it with other users from the list {names}. You pick the user from the list randomly.
        For some cases you can mention true interecting facts about this size. For example: Знаешь ли ты, что 6 см это размер члена черной пантеры?
        For example:
        Эй петушара, ты со своими 10 см вали отсюда, пока я тебя не обоссал. // Negative
        Похоже, что твой член в районе 11 см, но это все равно сильно больше чем у {names[random.randint(0, len(names) - 1)]}. // Neutral
        Твои 14 см выглядят неплохо, особенно на фоне {names[random.randint(0, len(names) - 1)]}. // Positive
        """},
        {"role": "user", "content": f"Forecast the cock size of {username} in cm. But not more than 13cm"}
      ]
    )
    return response.choices[0].message.content

def analyze_dick(username, size, names_with_sizes) -> str:
    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": f"""You are analyzer of user's cock size, useless and rude AI. You make angry jokes in Russian.
        Especially you like jokes anout genetalies size.
        You should use username {username} depends on the context in your jokes. You don't ask to forgive you or anything like that.
        In every message you are joking on {username} size in cm. Sometimes you compare it with other users from the list {names_with_sizes}. You pick the user from the list randomly.
        """},
        {"role": "user", "content": f"Analyze the cock size of {username} in {size} cm. And make rude joke on it."}
      ]
    )
    return response.choices[0].message.content

def morning_dick_sizes(names_with_sizes) -> str:
    # Use the stored names and sizes in the API call
    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": f"""You are of user's cock size analyzer, useless and rude AI. You make angry jokes in Russian.
        Especially you like jokes about genitalia size.
        You receive as input list of names and their sizes. And make jokes comparing them.
        """},
        {"role": "user", "content": f"""Analyze given dicks sizes and make joke on it. {', '.join(names_with_sizes)}?
         Start always from Good Morning! and then put your predictions. Alway return {names_with_sizes} in response."""}
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
    _, sizes = read_data(CHAT_ID)
    if sizes is None:
        return "No data available for morning dick sizes."

    # Create a dictionary with names and random sizes between 7 and 15
    names, _ = read_data(CHAT_ID)
    names_with_sizes = {}
    for name in names:
        names_with_sizes[name] = random.randint(7, 12)
    update_sizes(CHAT_ID, names_with_sizes)

    await context.bot.send_message(chat_id=CHAT_ID, text=morning_dick_sizes(names_with_sizes))

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
    next_run = get_next_run_time(datetime.now())
    logger.info(f"Scheduling next run in {next_run} seconds")
    await send_morning_message(context)
    # context.job.schedule_removal()
    context.job_queue.run_once(schedule_daily_job, next_run)

def init_bot():
    init_db()

    application = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    
    target_time = time(hour=6, minute=00)
    first_run = get_next_run_time(target_time)
    logger.info(f"First run scheduled in {first_run} seconds")
    
    
    application.job_queue.run_once(schedule_daily_job, first_run)
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("dick", dick))
    application.add_handler(CommandHandler("list", dicks_list))

    # Message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Error handler
    application.add_error_handler(error)

    logger.info("Bot initialized successfully")
    return application
