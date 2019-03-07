from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram.error import TimedOut
from settings import Settings
from strings import Strings

queue = []

def enqueue(callback, *args, **kwargs):
    queue.append([callback, args, kwargs])

def exec():
    global queue
    while len(queue):
        callback, args, kwargs = queue[0]
        try:
            callback(*args, **kwargs)
        except TimedOut:
            print('Timed out, but we should somehow just let it go.')
        queue.pop(0)

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
