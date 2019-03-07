from enum import Enum
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from settings import Settings
from strings import Strings

suits = {
    'Clubs': '♣',
    'Diamonds': '♦',
    'Hearts': '♥',
    'Spades': '♠'
}

ranks = [None, 'A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

class Card:
    class Suit(Enum):
        Clubs = 1
        Diamonds = 2
        Hearts = 3
        Spades = 4

    def __init__(self, game, suit, rank):
        self.game = game
        if type(suit) is int:
            self.suit = self.Suit(suit)
        elif type(suit) is str:
            self.suit = self.Suit[suit]
        else:
            raise
        self.rank = rank

    def __str__(self):
        return suits[self.suit.name] + ranks[self.rank]

    def discharge(self, player):
        if self.suit is self.Suit.Spades and self.rank == 1:
            self.game.value = 0
        elif self.rank == 4:
            self.game.direction *= -1
        elif self.rank == 5:
            return self.ask_players(player)
        elif self.rank == 10:
            return self.ask_ten(player)
        elif self.rank == 11:
            return True
        elif self.rank == 12:
            return self.ask_twenty(player)
        elif self.rank == 13:
            self.game.value = 99
        else:
            self.game.value += self.rank
        return True

    def is_available(self):
        return self.suit is self.Suit.Spades and self.rank == 1 or self.rank == 4 or self.rank == 5 or self.rank >= 10 or self.game.value + self.rank <= 99

    def ask_players(self, current_player):
        if len(self.game.players) > 2:
            current_player.send_message(Strings.ASK_DESIGNATE,
                    reply_markup = InlineKeyboardMarkup([[
                        InlineKeyboardButton(player.user.first_name, callback_data = 'choose ' + str(i)) for i, player in enumerate(self.game.players) if player.user.id != current_player.user.id]]))
            return False
        return True

    def ask_ten(self, player):
        if self.game.value < 10:
            self.game.value += 10
        elif self.game.value >= 90:
            self.game.value -= 10
        else:
            player.send_message(Strings.ASK_TEN,
                    reply_markup = InlineKeyboardMarkup([[
                        InlineKeyboardButton(ten, callback_data = 'choose ' + str(i)) for i, ten in enumerate(['+10', '-10'])]]))
            return False
        return True

    def ask_twenty(self, player):
        if self.game.value < 20:
            self.game.value += 20
        elif self.game.value >= 80:
            self.game.value -= 20
        else:
            player.send_message(Strings.ASK_TWENTY,
                    reply_markup = InlineKeyboardMarkup([[
                        InlineKeyboardButton(twenty, callback_data = 'choose ' + str(i)) for i, twenty in enumerate(['+20', '-20'])]]))
            return False
        return True

    def choose(self, player, idx):
        if self.rank == 5:
            self.game.current = idx - self.game.direction
            self.game.send_message(Strings.DESIGNATED.format('@' + player.user.username, '@' + self.game.players[idx].user.username))
        elif self.rank == 10:
            if idx == 0:
                self.game.value += 10
            elif idx == 1:
                self.game.value -= 10
            else:
                raise
        elif self.rank == 12:
            if idx == 0:
                self.game.value += 20
            elif idx == 1:
                self.game.value -= 20
            else:
                raise
        else:
            raise
