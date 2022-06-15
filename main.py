import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes, Updater
from telegram import __version__ as TG_VER

import os
PORT = int(os.environ.get('PORT', 5000))

TOKEN = '5494892715:AAGT2IZTYi__o3H6BPAbCtwwVo3AzRzRSME'

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

CHOICE, POINTS = range(2)
track_points = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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

async def choice(update: Update,  context: ContextTypes.DEFAULT_TYPE):
    "Based on Choice, exit programme or gets points inputted"
    reply_keyboard = [["200", "400", "600", "800", "1000"]]
    user = update.message.from_user
    logger.info(f"{user.first_name} chose {update.message.text}")
    if update.message.text.lower() == 'no':
        await update.message.reply_text(
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

async def points(update: Update,  context: ContextTypes.DEFAULT_TYPE):

    "Add points based on reply"
    user = update.message.from_user
    logger.info(f"{user.first_name} has given {update.message.text} points")
    global track_points
    track_points += int(update.message.text)
    await update.message.reply_text(
        f"Jun now has {track_points} points. FKS"
    )
    return ConversationHandler.END

async def cancel(update: Update,  context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "I guess Si Jun doesn't deserve points today:<", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

if __name__ == '__main__':
    application = ApplicationBuilder().token('5494892715:AAEy7HOZ-jx2cbwn2A6IMGTWvJ2QCyItBN0').build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOICE: [MessageHandler(filters.Regex("^(?:Yes|No)$"), choice)],
            POINTS: [MessageHandler(filters.Regex("^200|400|600|800|1000$"), points)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    Updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    Updater.bot.setWebhook('https://immense-anchorage-33732.herokuapp.com/' + TOKEN)