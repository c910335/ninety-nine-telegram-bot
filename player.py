from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from settings import Settings
from strings import Strings
from ext import enqueue

class Player:
    def __init__(self, bot, game, user, chat):
        self.bot = bot
        self.game = game
        self.user = user
        self.chat = chat
        self.hand = []
        self.card = None

    def str_hand(self):
        return ' '.join([str(card) for card in self.hand])

    def show_hand(self):
        enqueue(self.bot.send_message, self.chat.id, Strings.HAND.format(self.str_hand()))

    def is_available(self):
        return any(card.is_available() for card in self.hand)

    def ask_discharge(self):
        enqueue(self.bot.send_message, self.chat.id, Strings.ASK_DISCHARGE.format(self.str_hand()),
                reply_markup = InlineKeyboardMarkup([[
                    InlineKeyboardButton(str(card), callback_data = 'discharge ' + str(i)) for i, card in enumerate(self.hand) if card.is_available()]]))

    def discharge(self, idx):
        self.card = self.hand[idx]
        enqueue(self.bot.send_message, Settings.CHAT_ID, Strings.DISCHARGED.format('@' + self.user.username, str(self.card)))
        self.hand.pop(idx)
        if self.card.discharge(self):
            self.post_turn()
            return True

    def choose(self, idx):
        self.card.choose(self, idx)
        self.post_turn()
    
    def post_turn(self):
        card = self.draw()
        enqueue(self.bot.send_message, self.chat.id, Strings.DRAW.format(str(card)))
        self.game.return_deck(self.card)
        self.card = None
        self.show_hand()

    def draw(self):
        card = self.game.draw()
        self.hand.append(card)
        return card

    def burst(self):
        enqueue(self.bot.send_message, self.chat.id, Strings.YOU_BURST)
        enqueue(self.bot.send_message, Settings.CHAT_ID, Strings.BURST.format('@' + self.user.username))

    def win(self):
        enqueue(self.bot.send_message, Settings.CHAT_ID, Strings.WIN.format('@' + self.user.username))
