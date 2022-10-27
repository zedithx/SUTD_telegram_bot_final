import datetime
import logging
import sched
from functools import wraps
from threading import Thread
from time import sleep

import gspread
import schedule
import telegram
from apscheduler.schedulers.blocking import BlockingScheduler
from oauth2client.service_account import ServiceAccountCredentials
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

"""CONNECTING TO GOOGLE SHEETS"""
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive.file',
         'https://www.googleapis.com/auth/drive']

path = '/app'

creds = ServiceAccountCredentials.from_json_keyfile_name(path + '/creds.json', scope)

client = gspread.authorize(creds)
sheet = client.open('Echo@Cove').worksheet('TrialRun')

"""initialising variables/bot"""
TOKEN = '5631416352:AAGNTPtHwtzZi3dEpywSRDLSzD7e9vJBYVA'
bot = telegram.Bot(token=TOKEN)
# Define no. of variables to be stored
NAME, STUDENT_ID, MUSIC_THEME, CONFIRMATION, SUBMIT = range(5)
# START --> NAME --> STUDENTID --> MUSIC THEME --> CONFIRMATION --> LOAD INTO GOOGLESHEETS --> SUBMIT

# store chat ids as key and inputs as values
userID_database = {}
musictheme_dict = {'1': "FEELIN' GOOD", '2': "2000s", '3': "HIPHOP"}

def send_typing_action(func):
    """Wrapper to show that bot is typing"""
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func

# Explains details of ECHO and ask if they would like to register
@send_typing_action
def start(update: Update, _: CallbackContext):
    """Starts the conversation and asks whether the user would like to register for Echo"""
    user = update.message.from_user
    userID = str(update.message.chat_id)
    if userID not in userID_database:
        userID_database[userID] = []
    elif userID_database[userID]:
        logger.info(f"{user.first_name} tried to register but is already registered in the system")
        update.message.reply_text(
            'You have already registered for Echo@Cove. Please contact @zedithx on telegram for support '
            'if the details that you had entered previously was incorrect', reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    logger.info(f"{user.first_name} has started the bot")

    bot.sendPhoto(update.message.chat_id, open("Images/Echo_main.jpg", 'rb'), caption=
        "Hello. Welcome to the Echo@Cove 2022 Registration Bot \n\n"
        "Echo@Cove is an event on 17 November where we have invited DJs to mix musics with 3 different themes\n\n"
        "These themes will be...")
    sleep(3)
    bot.sendPhoto(update.message.chat_id, open("Images/Echo_details.jpg", 'rb'), caption="FEELIN' GOOD")
    sleep(3)
    bot.sendPhoto(update.message.chat_id, open("Images/Echo_details.jpg", 'rb'), caption='2000s')
    sleep(3)
    bot.sendPhoto(update.message.chat_id, open("Images/Echo_details.jpg", 'rb'), caption='HIP HOP')
    sleep(3)
    update.message.reply_text(
        "We will be giving out glowsticks based on the theme that u choose. \n\n"
        "The main goal of this event is to allow everyone to bond with each other based on the music theme they enjoy "
        "the most out of the 3 themes \n\n"
        "Come along and sign up now to socialise with more people and just have a great time overall!"
    )
    sleep(3)
    reply_keyboard = [["Yes", "No"]]
    update.message.reply_text(
        "Do you consent to the collection, use or disclosure of your personal data only for the purpose of this event?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard)
    )
    return NAME

# Get Name
@send_typing_action
def name(update: Update, _: CallbackContext):
    """Prompt user to enter name"""
    user = update.message.from_user
    if update.message.text.lower() == 'no':
        logger.info(f"{user.first_name} has rejected the PDPA clause")
        update.message.reply_text("Please consent to the PDPA clause to proceed with registering!",
                                  reply_markup=ReplyKeyboardRemove())
        logger.info(f"{userID_database=}")
        return ConversationHandler.END
    elif update.message.text.lower() == 'yes':
        logger.info(f"{user.first_name} has indicated interest in registering")
        update.message.reply_text(
            'Please enter your full name.', reply_markup=ReplyKeyboardRemove())
        return STUDENT_ID


# Get Student Id
@send_typing_action
def student_id(update: Update, _: CallbackContext):
    """Prompt user to enter Student ID"""
    user = update.message.from_user
    logger.info(f"{user.first_name} has indicated entered his/her name")
    userID = str(update.message.chat_id)
    userID_database[userID].append(update.message.text)
    update.message.reply_text(
            'Now please enter your Student ID.', reply_markup=ReplyKeyboardRemove())
    return MUSIC_THEME

# Get favourite music theme
@send_typing_action
def music_theme(update: Update, _: CallbackContext):
    """Prompt user to choose favourite music theme"""
    user = update.message.from_user
    userID = str(update.message.chat_id)
    try:
        int(update.message.text)
    except:
        logger.info(f"{user.first_name} has entered an invalid student id")
        update.message.reply_text(
            'You did not enter a valid Student ID.\n'
            'Please register with the right Student ID again.', reply_markup=ReplyKeyboardRemove()
        )
        userID_database[userID].clear()
        logger.info(f"{userID_database=}")
        return ConversationHandler.END
    logger.info(f"{user.first_name} has indicated entered his/her student id")
    userID_database[userID].append(update.message.text)
    reply_keyboard = [['1', '2', '3']]
    update.message.reply_text(
        'Now please choose your favourite theme out of the 3. \n'
        "1: FEELIN' GOOD \n"
        '2: 2000s \n'
        '3: HIPHOP \n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    return CONFIRMATION

@send_typing_action
def confirmation(update: Update, _: CallbackContext):
    """Prompt user to confirm his details after entering all his particulars"""
    user = update.message.from_user
    logger.info(f"{user.first_name} has indicated entered his/her preference for music theme")
    userID = str(update.message.chat_id)
    userID_database[userID].append(musictheme_dict[update.message.text])
    update.message.reply_text('Please check your details before submitting.\n\n')
    update.message.reply_text(
        'Name: ' + userID_database[userID][0] + '\n'
        'Student ID: ' + userID_database[userID][1] + '\n'
        'Favourite Music Theme: ' + userID_database[userID][2])
    reply_keyboard = [['Yes', 'No']]
    update.message.reply_text('Are the details that you entered correct? \n \n'
                              'Enter Yes or No.',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return SUBMIT


@send_typing_action
def submit(update: Update, _:CallbackContext):
    """Store details in savedindex dict as well as google sheets after user has confirmed details are correct"""
    userID = str(update.message.chat_id)
    if update.message.text.lower() == 'yes':
        # Program to add to GOOGLE SHEETS HERE!
        Name = userID_database[userID][0]
        StudentID= userID_database[userID][1]
        MusicTheme = userID_database[userID][2]
        client = gspread.authorize(creds)
        sheet = client.open('Echo@Cove').worksheet('TrialRun')
        data = sheet.get_all_records()
        row_to_insert = [Name, StudentID, MusicTheme]
        # userID_savedindex[userID] = len(data) + 2
        sheet.insert_row(row_to_insert, len(data) + 2)
        update.message.reply_text(
            'Registration completed! \n'
            'We hope you will have fun in this event!\n'
            'Do look out for any updates nearing to the event from this telegram bot!\n'
            'We will see you on the 17th of November!'
        )
        logger.info(f"{userID_database=}")
        return ConversationHandler.END
    # if information is incorrect, remove from the database dictionary and end conversation
    else:
        update.message.reply_text(
            'Registration is cancelled. \n'
            'Please start the bot again and enter the right particulars', reply_markup=ReplyKeyboardRemove())
        userID_database[userID].clear()
        logger.info(f"{userID_database=}")
        return ConversationHandler.END
@send_typing_action
def cancel(update: Update, _: CallbackContext):
    """Cancels and ends the conversation."""
    userID = str(update.message.chat_id)
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        "We hope that you will eventually join ECHO @ Cove!", reply_markup=ReplyKeyboardRemove()
    )
    userID_database[userID].clear()
    logger.info(f"{userID_database=}")
    return ConversationHandler.END



if __name__ == '__main__':

    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(Filters.regex('(?i)^(yes|no)$'), name)],
            STUDENT_ID: [MessageHandler(Filters.regex("(.*?)"), student_id)],
            MUSIC_THEME: [MessageHandler(Filters.regex("(.*?)"), music_theme)],
            CONFIRMATION: [MessageHandler(Filters.regex('^[1-3]$'), confirmation)],
            SUBMIT: [MessageHandler(Filters.regex('(?i)^(yes|no)$'), submit)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dispatcher.add_handler(start_conv_handler)
    dispatcher.add_handler(CommandHandler('cancel', cancel))

    test = updater.start_webhook(listen="0.0.0.0",
                                 port=PORT,
                                 url_path=TOKEN,
                                 webhook_url='https://gentle-plains-09954.herokuapp.com/' + TOKEN)
    updater.idle()

