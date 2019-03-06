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
            print('Timed out. Let\'s retry!')
            continue
        queue.pop(0)

def handle(handler_type, callback, name = None):
    def handler(bot, update):
        try:
            print(update.message or update.callback_query)
            callback(bot, update)
            exec()
        except Exception as e:
            print(e)
            message = update.message or update.callback_query.message
            message.reply_text(Strings.FAIL)
    if handler_type == 'command':
        return CommandHandler(name or callback.__name__, handler)
    elif handler_type == 'callback_query':
        return CallbackQueryHandler(handler, pattern = name or callback.__name__)
    else:
        raise
