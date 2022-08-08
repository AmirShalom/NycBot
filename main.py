import logging
import os
import sys
import telegram
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)
from bathrooms import bathrooms_ops
from markets import markets_ops
from wifi import wifi_ops

sys.path.append("/home/shalom/openData/bot/markets")
sys.path.append("/opt/NycBot/src/wifi")
sys.path.append("/opt/NycBot/src/bathrooms")


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

START_BOT, MASTER_BOT, GET_BATHROOM_DATA, GET_MARKETS_DATA, GET_WIFI_DATA = range(5)


def start_bot(update, context):
    logging.info('Starting NYC bot')
    entry_msg = 'Welcome to the NYC bot \U0001F306 \n\
Please select the service you would like to get today: \n\n\
\U0001F33D Farmers Markets bot - Getting the farmers markets in NYC by day or the closest \n\n\
\U0001F4F6 Wifi bot - Getting the 5 closest free Wifi spots to your location \n\n\
\U0001F6BE Public Bathroom Bot - Getting the 5 closet public bathrooms to your location'

    menu = [
        [InlineKeyboardButton('Farmers Markets Bot', callback_data='markets')],
        [InlineKeyboardButton('Wifi Bot', callback_data=f"wifi")],
        [InlineKeyboardButton('Public Bathroom Bot', callback_data=f"bathroom")]
    ]
    reply_markup = InlineKeyboardMarkup(menu)
    update.message.reply_text(text=entry_msg, reply_markup=reply_markup)

    return MASTER_BOT


def master_bot(update, context):
    logging.info('Getting user input from main menu')
    if update.callback_query:
        query = update.callback_query
        logging.info('User input is: {}'.format(query['data']))
        logging.info('Starting {} bot'.format(query['data']))
        global bot_name

        if query['data'] == 'markets':
            bot_name = 'markets_bot'
            markets_ops.show_days(update, context)
            return GET_MARKETS_DATA
        if query['data'] == 'wifi':
            bot_name = 'wifi_bot'
            return GET_WIFI_DATA
        if query['data'] == 'bathroom':
            bot_name = 'bathroom_bot'
            return GET_BATHROOM_DATA


def location(update, context):
    logging.info('Getting user location')
    if update.edited_message:
        message = update.edited_message
    else:
        message = update.message
    if 'bot_name' in globals():
        logging.info("bot name is {} for location detector".format(bot_name))
        try:
            user_latitude = message.location.latitude
            user_longitude = message.location.longitude
            if bot_name == 'wifi_bot':
                wifi_ops.calculate_closest(update, context, user_latitude=user_latitude, user_longitude=user_longitude)
            elif bot_name == 'markets_bot':
                markets_ops.calculate_closest(update, context, user_latitude=user_latitude, user_longitude=user_longitude)
            elif bot_name == 'bathroom_bot':
                bathrooms_ops.calculate_closest(update, context, user_latitude=user_latitude, user_longitude=user_longitude)
            return cancel(update, context)
        except AttributeError:
            logging.warning('User location is not shared with the bot')
            query = update.callback_query
            query.edit_message_text(
            text='Cannot get the closest market.\nPlease share your location with the bot and start the bot again '
                'using the /start option')
            return ConversationHandler.END


def cancel(update, context):
    logging.info('Exiting the bot')
    query = update.callback_query
    query.answer()
    query.edit_message_text("\nThank you for using the NycBot :)\n\
To re-run the bot, please type:\n/start")

    return ConversationHandler.END


def main():
    updater = Updater(TELEGRAM_API_TOKEN, use_context=True)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_bot)],
        states={
            MASTER_BOT: [CallbackQueryHandler(master_bot)],
            GET_MARKETS_DATA: [CallbackQueryHandler(markets_ops.fetch_data)],
            GET_WIFI_DATA: [CallbackQueryHandler(wifi_ops.fetch_data)],
            GET_BATHROOM_DATA: [CallbackQueryHandler(bathrooms_ops.fetch_data)]
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