from telegram.ext import Updater
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from settings import Settings
from strings import Strings
from bot import enqueue, send_message, send_group_message, add_handler, run
from game import Game

game = Game()
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
        enqueue(update.message.reply_text, Strings.JOINED)
        send_group_message(Strings.NAMED_JOINED.format('@' + update.message.from_user.username))
        if status is game.Status.PREPARING and game.status is game.Status.OPEN:
            enqueue(join_message.edit_text, Strings.JOIN, reply_markup = join_reply_markup)
            send_message(update.message.chat.id, Strings.START,
                    reply_markup = InlineKeyboardMarkup([[
                        InlineKeyboardButton(Strings.START_BUTTON, callback_data = 'start')]]))

def abort(bot, update):
    if update.message.chat.id == Settings.CHAT_ID:
        game.abort(update.message.from_user)
        enqueue(update.message.reply_text, Strings.ABORT)

def start(bot, update):
    game.start(update.callback_query.from_user)
    enqueue(join_message.edit_reply_markup)
    enqueue(update.callback_query.edit_message_reply_markup)
    send_group_message(Strings.STARTED)
    game.next()

def rule(bot, update):
    enqueue(update.message.reply_text, Strings.RULE, parse_mode = 'Markdown')

def discharge(bot, update):
    game.discharge(update.callback_query.from_user, int(update.callback_query.data[-1]))
    enqueue(update.callback_query.edit_message_reply_markup)

def choose(bot, update):
    game.choose(update.callback_query.from_user, int(update.callback_query.data[-1]))
    enqueue(update.callback_query.edit_message_reply_markup)

def resume(bot, update):
    return

add_handler('command', hello)
add_handler('command', new)
add_handler('command', abort)
add_handler('command', join, 'start')
add_handler('callback_query', start)
add_handler('command', rule)
add_handler('callback_query', discharge, '^discharge \d$')
add_handler('callback_query', choose, '^choose \d$')
add_handler('command', resume)
run()
