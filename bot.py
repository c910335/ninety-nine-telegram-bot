from queue import Queue
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram.error import TimedOut
from settings import Settings
from strings import Strings

updater = Updater(Settings.API_TOKEN)
queue = Queue()
bot = updater.bot

def enqueue(callback, *args, **kwargs):
    queue.put([callback, args, kwargs])

def exec():
    global queue
    while queue.qsize():
        callback, args, kwargs = queue.get()
        try:
            callback(*args, **kwargs)
        except TimedOut:
            print('Timed out, but we should somehow just let it go.')

def send_message(chat_id, text, *args, **kwargs):
    enqueue(bot.send_message, chat_id, text, *args, **kwargs)

def send_group_message(text, *args, **kwargs):
    send_message(Settings.CHAT_ID, text, *args, **kwargs)

def handle(handler_type, callback, name = None):
    def handler(bot, update):
        message_or_callback_query = update.message or update.callback_query
        message = update.message or update.callback_query.message
        text_or_data = update.message and update.message.text or update.callback_query.data
        user = message_or_callback_query.from_user
        try:
            print('@{} ({} {}): {}'.format(user.username, message.chat.type.capitalize(), type(message_or_callback_query).__name__, text_or_data))
            callback(bot, update)
            exec()
        except Exception as e:
            print('({}) {}'.format(type(e).__name__, str(e)))
            bot.send_message(Settings.ADMIN_ID, '@{} ({} {}): ({}) {}'.format(user.username, message.chat.type.capitalize(), type(message_or_callback_query).__name__, type(e).__name__ , str(e)))
    if handler_type == 'command':
        return CommandHandler(name or callback.__name__, handler)
    elif handler_type == 'callback_query':
        return CallbackQueryHandler(handler, pattern = name or callback.__name__)
    else:
        raise

def add_handler(handler_type, callback, name = None):
    updater.dispatcher.add_handler(handle(handler_type, callback, name))

def run():
    updater.start_polling()
    print('Bot is running.')
    updater.idle()
