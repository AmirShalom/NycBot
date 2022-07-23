import json
import os
from sodapy import Socrata
import telegram
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

SHOW_DATA, GET_DATA = 0, 1


def show_days(update, context):
    days = [
    [InlineKeyboardButton('Sunday', callback_data=f"Sunday")],
    [InlineKeyboardButton('Monday', callback_data=f"Monday")],
    [InlineKeyboardButton('Tuesday', callback_data=f"Tuesday")],
    [InlineKeyboardButton('Wednesday', callback_data=f"Wednesday")],
    [InlineKeyboardButton('Thursday', callback_data=f"Thursday")],
    [InlineKeyboardButton('Friday', callback_data=f"Friday")],
    [InlineKeyboardButton('Saturday', callback_data=f"Saturday")]
    ]
    reply_markup = InlineKeyboardMarkup(days)
    update.message.reply_text(f"""
    Welcome to the NYC farmers' markets bot,
Please select a day and I will show what farmers' markets we have that day.
    """, reply_markup=reply_markup)

    return GET_DATA

def cancel(update, context):
    print('bye')


def fetch_data(update, context):
    query = update.callback_query
    message = "The farmers' market opened on {} are: \n".format(query['data'])
    OPENDATA_API_TOKEN = os.getenv('OPENDATA_API_TOKEN')
    client = Socrata("data.cityofnewyork.us", os.getenv(OPENDATA_API_TOKEN))
    results = client.get("8vwk-6iz2")
    for market in results:
        if market['daysoperation'] == query['data']:
            message += "{} @ {}\n".format(market['streetaddress'], market['hoursoperations'])
    query.edit_message_text(parse_mode=telegram.ParseMode.HTML, text=message)


def main():
    updater = Updater(TELEGRAM_API_TOKEN, use_context=True)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', show_days)],

        states={
            SHOW_DATA: [
                        CommandHandler('start', show_days),
                    ],
            GET_DATA: [
                        CallbackQueryHandler(fetch_data)
                    ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    # updater.idle()


if __name__ == '__main__':
    TELEGRAM_API_TOKEN = os.environ.get('TELEGRAM_API_TOKEN')
    bot = telegram.Bot(token=TELEGRAM_API_TOKEN)
    main()

