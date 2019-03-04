from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from settings import Settings
from strings import Strings
from game import Game

updater = Updater(Settings.API_TOKEN)
game = Game(updater.bot)

join_message = None
join_reply_markup = None

def hello(bot, update):
    update.message.reply_text('hello, {}'.format(update.message.from_user.first_name))

def new(bot, update):
    global join_message
    global join_reply_markup
    if update.message.chat.id == Settings.CHAT_ID:
        game.new(update.message.from_user)
        update.message.reply_text(Strings.NEW)
        join_reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(Strings.JOIN_BUTTON, url = Settings.BOT_URL + '?start=join')]])
        join_message = bot.send_message(Settings.CHAT_ID, Strings.ADMIN_JOIN.format('@' + update.message.from_user.username), reply_markup = join_reply_markup)

def join(bot, update):
    if update.message.chat.type == 'private' and update.message.text == '/start join':
        status = game.status
        game.add_player(update.message.from_user, update.message.chat)
        update.message.reply_text(Strings.JOINED)
        bot.send_message(Settings.CHAT_ID, Strings.NAMED_JOINED.format('@' + update.message.from_user.username))
        if status is game.Status.PREPARING and game.status is game.Status.OPEN:
            join_message.edit_text(Strings.JOIN, reply_markup = join_reply_markup)
            bot.send_message(update.message.chat.id, Strings.START,
                    reply_markup = InlineKeyboardMarkup([[
                        InlineKeyboardButton(Strings.START_BUTTON, callback_data = 'start')]]))

def abort(bot, update):
    if update.message.chat.id == Settings.CHAT_ID:
        game.abort(update.message.from_user)
        update.message.reply_text(Strings.ABORT)

def start(bot, update):
    game.start(update.callback_query.from_user)
    join_message.edit_reply_markup()
    update.callback_query.edit_message_reply_markup()
    bot.send_message(Settings.CHAT_ID, Strings.STARTED)
    game.next()

def discharge(bot, update):
    game.discharge(update.callback_query.from_user, int(update.callback_query.data[-1]))
    update.callback_query.edit_message_reply_markup()

def choose(bot, update):
    game.choose(update.callback_query.from_user, int(update.callback_query.data[-1]))
    update.callback_query.edit_message_reply_markup()

def handle(handler_type, callback, name = None):
    def handler(bot, update):
        try:
            print(update.message or update.callback_query)
            callback(bot, update)
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

updater.dispatcher.add_handler(handle('command', hello))
updater.dispatcher.add_handler(handle('command', new))
updater.dispatcher.add_handler(handle('command', abort))
updater.dispatcher.add_handler(handle('command', join, 'start'))
updater.dispatcher.add_handler(handle('callback_query', start))
updater.dispatcher.add_handler(handle('callback_query', discharge, '^discharge \d$'))
updater.dispatcher.add_handler(handle('callback_query', choose, '^choose \d$'))

updater.start_polling()
print('Bot is start running.')
updater.idle()
