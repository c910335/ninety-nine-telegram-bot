from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from settings import Settings
from strings import Strings
from ext import enqueue

class Player:
    def __init__(self, game, user, chat):
        self.game = game
        self.user = user
        self.chat = chat
        self.hand = []
        self.card = None

    def str_hand(self):
        return ' '.join([str(card) for card in self.hand])

    def send_message(self, text, *args, **kwargs):
        enqueue(self.game.bot.send_message, self.chat.id, text, *args, **kwargs)

    def show_hand(self):
        self.send_message(Strings.HAND.format(self.str_hand()))

    def is_available(self):
        return any(card.is_available() for card in self.hand)

    def ask_discharge(self):
        self.send_message(Strings.ASK_DISCHARGE.format(self.str_hand()),
                reply_markup = InlineKeyboardMarkup([[
                    InlineKeyboardButton(str(card), callback_data = 'discharge ' + str(i)) for i, card in enumerate(self.hand) if card.is_available()]]))

    def discharge(self, idx):
        self.card = self.hand[idx]
        self.send_message(Strings.YOU_DISCHARGED.format(str(self.card)))
        self.game.send_message(Strings.DISCHARGED.format('@' + self.user.username, str(self.card)), without = self)
        self.hand.pop(idx)
        if self.card.discharge(self):
            self.post_turn()
            return True

    def choose(self, idx):
        self.card.choose(self, idx)
        self.post_turn()
    
    def post_turn(self):
        card = self.draw()
        self.send_message(Strings.DRAW.format(str(card)))
        self.game.return_deck(self.card)
        self.card = None
        self.show_hand()

    def draw(self):
        card = self.game.draw()
        self.hand.append(card)
        return card

    def burst(self):
        self.send_message(Strings.YOU_BURST)
        self.game.send_message(Strings.BURST.format('@' + self.user.username), without = self)

    def win(self):
        self.send_message(Strings.YOU_WIN)
        self.game.send_message(Strings.WIN.format('@' + self.user.username), without = self)
