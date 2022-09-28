import logging
from functools import wraps

import telegram
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, ChatAction
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, \
    Updater, Filters, CallbackContext
from telegram import __version__ as TG_VER

import os
PORT = int(os.environ.get('PORT', '8443'))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

TOKEN = '5494892715:AAEieqoP3Ga4rJnwmopCeb3IXolWqvXPYjc'
bot = telegram.Bot(token=TOKEN)
CHOICE, POINTS, SET_GOAL, PLANS, ANSWER = range(5)
track_points = 40400
goal = 100000

# Show that bot it "TYPING"
def send_typing_action(func):
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func
@send_typing_action
def start(update: Update, _: CallbackContext):
    """Starts the conversation and asks what does user want to do."""
    user = update.message.from_user
    logger.info(f"{user.first_name} has started the bot")
    reply_keyboard = [["Yes", "No"]]

    update.message.reply_text(
        "Hallo! I'm here to assist u with giving points to Si Jun \n"
        "Send /cancel to stop talking to me.\n\n"
        "Would u like to add friendship points for Si Jun???!!!",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Yes or No?"
        ),
    )
    return CHOICE
@send_typing_action
def affection(update: Update, _: CallbackContext):
    """Ask whether affection is needed"""
    reply_keyboard = [["Yes", "No"]]

    update.message.reply_text(
        "Are u missing Si Jun? \n"
        "Do u need some affection from him?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Yes or No?"
        ),
    )
    return ANSWER
@send_typing_action
def affection_message(update: Update, _: CallbackContext):
    """Shows photos and affection"""
    user = update.message.from_user
    logger.info(f"{user.first_name} has chosen the affection option")
    update.message.reply_text(
        f"Hello I love u and miss u too!! Heres some cute photos to make u feel better!"
    )
    bot.sendPhoto(update.message.chat_id, open("Images/sijun.JPG", 'rb'), caption=
    'Picture of me being stupid!')
    bot.sendPhoto(update.message.chat_id, open("Images/tgt.JPG", 'rb'), caption=
    'Picture of us tgt!')
    bot.sendPhoto(update.message.chat_id, open("Images/sarah.JPG", 'rb'), caption=
    'Picture of u being stupid!')
    bot.sendPhoto(update.message.chat_id, open("Images/rhino.jpeg", 'rb'), caption=
    'Picture of rhino!!!')
    return ConversationHandler.END


"""Progress choice"""
@send_typing_action
def progress(update:Update, _: CallbackContext):
    "returns progress of friendship points"
    user = update.message.from_user
    ratio = int(track_points/goal*10)
    bar = '█' * ratio
    logger.info(f"{user.first_name} has checked the progress bar")
    update.message.reply_text(
        f"{bar} \n"
        f"Points: {track_points}/{goal}\n"
        "Goal: Have a nice meal with rhino looking at his relatives in the zoo!"
    )
    return ConversationHandler.END

"""Set Goal choice"""
@send_typing_action
def choose_goal(update: Update, _: CallbackContext):

    "Add points based on reply"
    global goal
    update.message.reply_text(
        f"Please set a goal for Jun"
    )
    return SET_GOAL

@send_typing_action
def set_goal(update: Update, _: CallbackContext):
    "Add points based on reply"
    user = update.message.from_user
    logger.info(f"{user.first_name} has set the goal to be {update.message.text} points")
    global goal
    if type(goal) != int:
        update.message.reply_text(
            f"{goal} is not a number!"
        )
        return ConversationHandler.END
    goal = int(update.message.text)
    update.message.reply_text(
        f"Thats quite high but okay FKS. Goal shall be {goal} now:<"
    )
    return ConversationHandler.END


"""Set Plans Choice"""
@send_typing_action
def set_plans(update: Update, _: CallbackContext):
    """Set plans and notify Si Jun"""
    reply_keyboard = [["Mon", "Tues", "Wed", "Thurs", "Fri", "Saturday", "Sunday"]]
    user = update.message.from_user
    logger.info(f"{user.first_name} is setting plans")
    update.message.reply_text(
        "Wed: 12pm onwards to night \n"
        "Thurs: Whole day +- gym",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="How many points?"
        ),
    )
    return PLANS
@send_typing_action
def confirm_plans(update: Update, _: CallbackContext):
    """Check if plans are available"""
    user = update.message.from_user
    if update.message.text.lower() == 'wed' or update.message.text.lower() == 'thurs':
        update.message.reply_text(
            "Ur plans have been made with Si Jun. Si Jun will confirm with u on text in abit on the timing!"
        )
        logger.info(f"{user.first_name} has set a date with you on the {update.message.text}")
    else:
        update.message.reply_text(
            "Please check the available dates again. It appears Si Jun is not free during that day :<"
        )
    return ConversationHandler.END

@send_typing_action
def choice(update: Update, _: CallbackContext):
    "Based on Choice, exit programme or gets points inputted"
    reply_keyboard = [["400", "800", "1200", "1600", "2000", "5000"]]
    user = update.message.from_user
    logger.info(f"{user.first_name} chose {update.message.text}")
    if update.message.text.lower() == 'no':
        update.message.reply_text(
            "Then u type /start for what bij?!!!", reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    else:
        update.message.reply_text(
            "How many points should Mr Yang get today?!!!",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="How many points?"
            ),
        )
    return POINTS
@send_typing_action
def points(update: Update, _: CallbackContext):

    "Add points based on reply"
    user = update.message.from_user
    logger.info(f"{user.first_name} has given {update.message.text} points")
    global track_points
    track_points += int(update.message.text)
    update.message.reply_text(
        f"Jun now has {track_points} points. FKS"
    )
    return ConversationHandler.END
@send_typing_action
def cancel(update: Update, _: CallbackContext):
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        "I guess Si Jun doesn't deserve points today:<", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END



if __name__ == '__main__':
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
    print('check')

    test = updater.start_webhook(listen="0.0.0.0",
                                 port=PORT,
                                 url_path=TOKEN,
                                 webhook_url='https://immense-anchorage-33732.herokuapp.com/' + TOKEN)

    print(test)
    updater.idle()
