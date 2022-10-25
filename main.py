import logging
from functools import wraps

import gspread
import telegram
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
# START --> NAME --> STUDENTID --> MUSIC THEME --> COMFIRMATION --> LOAD INTO GOOGLESHEETS --> SUBMIT
userID_database = {}
userID_savedindex = {}

def send_typing_action(func):
    """Wrapper to show that bot is typing"""
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func

# Explains details of the MusicFest event and ask if they would like to register
@send_typing_action
def start(update: Update, _: CallbackContext):
    """Starts the conversation and asks whether the user would like to register for the MusicFest"""
    user = update.message.from_user
    userID = str(update.message.chat_id)
    if userID not in userID_database:
        userID_database[userID] = []
    logger.info(f"{user.first_name} has started the bot")

    update.message.reply_text(
        "Hello. Welcome to the Echo@Cove 2022 Registration Bot \n"
        "Echo@Cove is an event on 18 November where we have invited DJs to mix musics with 3 different themes\n"
        "These 3 themes will be..."
    )
    # bot.sendPhoto(update.message.chat_id, open("file name", 'rb'), caption='placeholder')
    # bot.sendPhoto(update.message.chat_id, open("file name", 'rb'), caption='placeholder')
    # bot.sendPhoto(update.message.chat_id, open("file name", 'rb'), caption='placeholder')
    update.message.reply_text(
        "We will be giving out wristbands based on the theme that u choose. \n"
        "The main goal of this event is to allow everyone to bond with each other based on the music theme they enjoy"
        "the most out of the 3 themes"
        "Come along and sign up now to socialise with more people and just have a great time overall!"
    )
    reply_keyboard = [["Yes", "No"]]
    update.message.reply_text(
        "Would you like to register for MusicFest 2022?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard)
    )
    return NAME

# Get Name
@send_typing_action
def name(update: Update, _: CallbackContext):
    """Prompt user to enter name"""
    user = update.message.from_user
    if update.message.text == 'No':
        logger.info(f"{user.first_name} has decided not to register")
        userID = str(update.message.chat_id)
        userID_database.pop(userID, None)
        return ConversationHandler.END
    elif update.message.text == 'Yes':
        logger.info(f"{user.first_name} has indicated interest in registering")
        update.message.reply_text(
            'Please enter your full name.', reply_markup=ReplyKeyboardRemove())
        return STUDENT_ID


# Get Student Id
@send_typing_action
def student_id(update: Update, _: CallbackContext):
    """Prompt user to enter Student ID"""
    userID = str(update.message.chat_id)
    userID_database[userID].append(update.message.text)
    update.message.reply_text(
            'Now please enter your Student ID.', reply_markup=ReplyKeyboardRemove())
    return MUSIC_THEME

# Get favourite music theme
@send_typing_action
def music_theme(update: Update, _: CallbackContext):
    """Prompt user to choose favourite music theme"""
    userID = str(update.message.chat_id)
    userID_database[userID].append(update.message.text)
    reply_keyboard = [['1', '2', '3']]
    update.message.reply_text(
        'Now please choose your favourite theme out of the 3. \n'
        '1: placeholder \n'
        '2: placeholder \n'
        '3: placeholder \n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    return CONFIRMATION

@send_typing_action
def confirmation(update: Update, _: CallbackContext):
    """Prompt user to confirm his details after entering all his particulars"""
    userID = str(update.message.chat_id)
    update.message.reply_text('Please check your details before submitting.\n')
    update.message.reply_text(
        'Name: ' + userID_database[userID][0] + '\n'
        'Student ID: ' + userID_database[userID][1] + '\n'
        'Favourite Music Theme' + userID_database[userID][2])
    reply_keyboard = [['Yes', 'No']]
    update.message.reply_text('Are the details that you entered correct? \n \n'
                              'Enter Yes or No.',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return SUBMIT


@send_typing_action
def submit(update: Update, _:CallbackContext):
    """Store details in savedindex dict as well as google sheets after user has confirmed details are correct"""
    if update.message.text.lower() == 'yes':
        print(userID_database)
        userID = str(update.message.chat_id)
        # Program to add to GOOGLE SHEETS HERE!
        Name = userID_database[userID][0]
        StudentID= userID_database[userID][1]
        MusicTheme = userID_database[userID][2]
        client = gspread.authorize(creds)
        sheet = client.open('placeholder').worksheet('placeholder')
        data = sheet.get_all_records()
        row_to_insert = [Name, StudentID, MusicTheme]
        userID_savedindex[userID] = len(data) + 2
        sheet.insert_row(row_to_insert, len(data) + 2)
        update.message.reply_text(
            '<b>Registration completed!</b> \n'
            'We hope you will have fun in this event!\n'
            'We will see you on the 17th of October!'
        )
        return ConversationHandler.END
    # if information is incorrect, remove from the database dictionary and end conversation
    else:
        update.message.reply_text(
            'Registration is cancelled. \n'
            'Please start the bot again and enter the right particulars')
        userID = str(update.message.chat_id)
        userID_database.pop(userID, None)
        return ConversationHandler.END
@send_typing_action
def cancel(update: Update, _: CallbackContext):
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        "We hope that you will eventually join this music festival!", reply_markup=ReplyKeyboardRemove()
    )
    # remove from the database dictionary
    userID = str(update.message.chat_id)
    userID_database.pop(userID, None)

    return ConversationHandler.END



if __name__ == '__main__':
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher


    start_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(Filters.text, name)],
            STUDENT_ID: [MessageHandler(Filters.text, name)],
            MUSIC_THEME: [MessageHandler(Filters.regex('^[1-5]$'), music_theme)],
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
