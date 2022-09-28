import logging

import telegram
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, \
    Updater, Filters
from telegram import __version__ as TG_VER

import os
PORT = int(os.environ.get('PORT', 5000))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

TOKEN = '5494892715:AAEieqoP3Ga4rJnwmopCeb3IXolWqvXPYjc'
CHOICE, POINTS, SET_GOAL, PLANS, ANSWER = range(5)
track_points = 40400
goal = 100000

async def start(update: Update, CallbackContext) -> int:
    """Starts the conversation and asks what does user want to do."""
    reply_keyboard = [["Yes", "No"]]

    await update.message.reply_text(
        "Hallo! I'm here to assist u with giving points to Si Jun \n"
        "Send /cancel to stop talking to me.\n\n"
        "Would u like to add friendship points for Si Jun???!!!",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Yes or No?"
        ),
    )
    return CHOICE

async def affection(update: Update, CallbackContext) -> int:
    """Ask whether affection is needed"""
    reply_keyboard = [["Yes", "No"]]

    await update.message.reply_text(
        "Are u missing Si Jun? \n"
        "Do u need some affection from him?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Yes or No?"
        ),
    )
    return ANSWER

async def affection_message(update: Update, CallbackContext) -> int:
    """Shows photos and affection"""
    user = update.message.from_user
    logger.info(f"{user.first_name} has chosen the affection option")
    await update.message.reply_text(
        f"Hello I love u and miss u too!! Heres some cute photos to make u feel better!"
    )
    await bot.sendPhoto(update.message.chat_id, open("Images/sijun.JPG", 'rb'), caption=
    'Picture of me being stupid!')
    await bot.sendPhoto(update.message.chat_id, open("Images/tgt.JPG", 'rb'), caption=
    'Picture of us tgt!')
    await bot.sendPhoto(update.message.chat_id, open("Images/sarah.JPG", 'rb'), caption=
    'Picture of u being stupid!')
    await bot.sendPhoto(update.message.chat_id, open("Images/rhino.jpeg", 'rb'), caption=
    'Picture of rhino!!!')
    return ConversationHandler.END


"""Progress choice"""
async def progress(update:Update, CallbackContext) -> int:
    "returns progress of friendship points"
    user = update.message.from_user
    ratio = int(track_points/goal*10)
    bar = '█' * ratio
    logger.info(f"{user.first_name} has checked the progress bar")
    await update.message.reply_text(
        f"{bar} \n"
        f"Points: {track_points}/{goal}\n"
        "Goal: Have a nice meal with rhino looking at his relatives in the zoo!"
    )
    return ConversationHandler.END

"""Set Goal choice"""
async def choose_goal(update: Update,  CallbackContext):

    "Add points based on reply"
    global goal
    await update.message.reply_text(
        f"Please set a goal for Jun"
    )
    return SET_GOAL

async def set_goal(update: Update, CallbackContext):
    "Add points based on reply"
    user = update.message.from_user
    logger.info(f"{user.first_name} has set the goal to be {update.message.text} points")
    global goal
    if type(goal) != int:
        await update.message.reply_text(
            f"{goal} is not a number!"
        )
        return ConversationHandler.END
    goal = int(update.message.text)
    await update.message.reply_text(
        f"Thats quite high but okay FKS. Goal shall be {goal} now:<"
    )
    return ConversationHandler.END

"""Set Plans Choice"""
async def set_plans(update: Update, CallbackContext):
    """Set plans and notify Si Jun"""
    reply_keyboard = [["Mon", "Tues", "Wed", "Thurs", "Fri", "Saturday", "Sunday"]]
    user = update.message.from_user
    logger.info(f"{user.first_name} is setting plans")
    await update.message.reply_text(
        "Wed: 12pm onwards to night \n"
        "Thurs: Whole day +- gym",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="How many points?"
        ),
    )
    return PLANS

async def confirm_plans(update: Update, CallbackContext):
    """Check if plans are available"""
    user = update.message.from_user
    if update.message.text.lower() == 'wed' or update.message.text.lower() == 'thurs':
        await update.message.reply_text(
            "Ur plans have been made with Si Jun. Si Jun will confirm with u on text in abit on the timing!"
        )
        logger.info(f"{user.first_name} has set a date with you on the {update.message.text}")
    else:
        await update.message.reply_text(
            "Please check the available dates again. It appears Si Jun is not free during that day :<"
        )
    return ConversationHandler.END

async def choice(update: Update,  CallbackContext):
    "Based on Choice, exit programme or gets points inputted"
    reply_keyboard = [["400", "800", "1200", "1600", "2000", "5000"]]
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

async def points(update: Update, CallbackContext):

    "Add points based on reply"
    user = update.message.from_user
    logger.info(f"{user.first_name} has given {update.message.text} points")
    global track_points
    track_points += int(update.message.text)
    await update.message.reply_text(
        f"Jun now has {track_points} points. FKS"
    )
    return ConversationHandler.END

async def cancel(update: Update, CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "I guess Si Jun doesn't deserve points today:<", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END



if __name__ == '__main__':
    bot = telegram.Bot(token=TOKEN)
    updater = Updater(TOKEN, use_context=True)
    # application = ApplicationBuilder().token('5494892715:AAEieqoP3Ga4rJnwmopCeb3IXolWqvXPYjc').build()
    dispatcher = updater.dispatcher


    start_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOICE: [MessageHandler(Filters.regex("^(?:Yes|No)$"), choice)],
            POINTS: [MessageHandler(Filters.regex("^400|800|1200|1600|2000|5000$"), points)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    goal_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("goal", choose_goal)],
        states={
            SET_GOAL: [MessageHandler(Filters.regex("(.*?)"), set_goal)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    affection_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("affection", affection)],
        states={
            ANSWER: [MessageHandler(Filters.regex("^(?:Yes|No)$"), affection_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    progress_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("progress", progress)],
        states={},
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    plans_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("plan", set_plans)],
        states={
            PLANS: [MessageHandler(Filters.regex("^(?:Mon|Tues|Wed|Thurs|Fri|Sat|Sun)$"), confirm_plans)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dispatcher.add_handler(start_conv_handler)
    dispatcher.add_handler(progress_conv_handler)
    dispatcher.add_handler(goal_conv_handler)
    dispatcher.add_handler(plans_conv_handler)
    dispatcher.add_handler(affection_conv_handler)

    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN,
                          webhook_url= 'https://afternoon-brook-87795.herokuapp.com/' + TOKEN)
