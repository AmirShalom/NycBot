import logging
import os
from sodapy import Socrata
import telegram
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

SHOW_DATA, GET_DATA, GET_LOCATION = 0, 1, 2


def show_days(update, context):
    menu = [
    [InlineKeyboardButton('Sunday', callback_data=f"Sunday")],
    [InlineKeyboardButton('Monday', callback_data=f"Monday")],
    [InlineKeyboardButton('Tuesday', callback_data=f"Tuesday")],
    [InlineKeyboardButton('Wednesday', callback_data=f"Wednesday")],
    [InlineKeyboardButton('Thursday', callback_data=f"Thursday")],
    [InlineKeyboardButton('Friday', callback_data=f"Friday")],
    [InlineKeyboardButton('Saturday', callback_data=f"Saturday")],
    [InlineKeyboardButton('Closest & Open', callback_data=f"closest_open")]
    ]
    reply_markup = InlineKeyboardMarkup(menu)
    update.message.reply_text(f"""
    Welcome to the NYC farmers' markets bot,
Please select a day and I will show what farmers' markets we have that day.
    """, reply_markup=reply_markup)

    return GET_DATA


def cancel(update, context):
    try:
        update.message.reply_text("Thank you for using the NycBot :)\n\
To re-run the bot, please type: /start")
    except:
        pass
    return ConversationHandler.END


def fetch_data(update, context):
    query = update.callback_query
    OPENDATA_API_TOKEN = os.getenv('OPENDATA_API_TOKEN')
    if query['data'] == 'closest_open':
        return location(update, context)
    else:
        message = "The farmers' market opened on {} are: \n\n".format(query['data'])
        client = Socrata("data.cityofnewyork.us", os.getenv(OPENDATA_API_TOKEN))
        results = client.get("8vwk-6iz2")
        for market in results:
            if market['daysoperation'] == query['data']:
                message += "** {} @ {}\n".format(market['streetaddress'], market['hoursoperations'])
        query.edit_message_text(parse_mode=telegram.ParseMode.HTML, text=message)
        return cancel(update, context)


def location(update, context):
    if update.edited_message:
        message = update.edited_message
    else:
        message = update.message
    user_location = (message.location.latitude, message.location.longitude)
    print(user_location)


def main():
    updater = Updater(TELEGRAM_API_TOKEN, use_context=True)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', show_days)],

        states={
            SHOW_DATA: [CommandHandler('start', show_days)],
            GET_DATA: [CallbackQueryHandler(fetch_data)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    location_handler = MessageHandler(Filters.location, location)
    dp = updater.dispatcher
    dp.add_handler(conv_handler)
    dp.add_handler(location_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    TELEGRAM_API_TOKEN = os.environ.get('TELEGRAM_API_TOKEN')
    bot = telegram.Bot(token=TELEGRAM_API_TOKEN)
    main()
