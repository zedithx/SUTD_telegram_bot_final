import asyncio
import logging
from asyncio import Queue

import telegram
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler,\
    Updater, CallbackContext, Filters
from telegram import __version__ as TG_VER

import os
PORT = int(os.environ.get('PORT', 5000))
TOKEN = '5494892715:AAGU1a7N0goUIyRT9qbX9j4jy6xqCHxgt0M'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

CHOICE, POINTS = range(2)
track_points = 0

async def start(update: Update, _: CallbackContext) -> int:
    """Starts the conversation and asks what does user want to do."""
    reply_keyboard = [["Yes", "No"]]

    await update.message.reply_text(
        "Hallo! I'm here to assist u with giving points to Si Jun! "
        "Send /cancel to stop talking to me.\n\n"
        "Would u like to add friendship points for Si Jun???!!!",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Yes or No?"
        ),
    )
    return CHOICE

async def choice(update: Update,  _: CallbackContext):
    "Based on Choice, exit programme or gets points inputted"
    reply_keyboard = [["200", "400", "600", "800", "1000"]]
    user = update.message.from_user
    logger.info(f"{user.first_name} chose {update.message.text}")
    if update.message.text.lower() == 'no':
        update.message.reply_text(
            "Then u type /start for what bij?!!!", reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "How many points should Mr Yang get today?!!!",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="How many points?"
            ),
        )
    return POINTS

async def points(update: Update,  _: CallbackContext):

    "Add points based on reply"
    user = update.message.from_user
    logger.info(f"{user.first_name} has given {update.message.text} points")
    global track_points
    track_points += int(update.message.text)
    await update.message.reply_text(
        f"Jun now has {track_points} points. FKS"
    )
    return ConversationHandler.END

async def cancel(update: Update,  _: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "I guess Si Jun doesn't deserve points today:<", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

if __name__ == '__main__':
    # application = ApplicationBuilder().token('5494892715:AAEy7HOZ-jx2cbwn2A6IMGTWvJ2QCyItBN0').build()
    bot = telegram.Bot(token=TOKEN)
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOICE: [MessageHandler(Filters.regex("^(?:Yes|No)$"), choice)],
            POINTS: [MessageHandler(Filters.regex("^200|400|600|800|1000$"), points)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dispatcher.add_handler(conv_handler)
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN, webhook_url='https://immense-anchorage-33732.herokuapp.com/' + TOKEN)