from enum import Enum
from random import sample
from settings import Settings
from strings import Strings
from ext import enqueue
from player import Player
from card import Card

class Game:
    class Status(Enum):
        OFF = 1
        PREPARING = 2
        OPEN = 3
        STARTED = 4

    def __init__(self, bot):
        self.status = self.Status.OFF
        self.players = []
        self.bot = bot

    def new(self, user):
        if self.status is self.Status.OFF:
            self.admin = user
            self.status = self.Status.PREPARING
        else:
            raise

    def abort(self, user):
        if self.status is not self.Status.OFF and Settings.ADMIN_ID == user.id or (self.status is self.Status.PREPARING or self.status is self.Status.OPEN) and self.admin.id == user.id:
            self.status = self.Status.OFF
            self.players = []
        else:
            raise

    def add_player(self, user, chat):
        if self.admin.id == user.id and self.status is self.Status.PREPARING and len(self.players) == 0:
            self.players.append(Player(self, user, chat))
            self.status = self.Status.OPEN
        elif self.status is self.Status.OPEN and not any(player.user.id == user.id for player in self.players):
            self.players.append(Player(self, user, chat))
        else:
            raise

    def send_message(self, text, *args, **kwargs):
        players = self.players.copy()
        if 'without' in kwargs:
            player = kwargs['without']
            del kwargs['without']
            players.remove(player)
        for player in players:
            enqueue(self.bot.send_message, player.chat.id, text, *args, **kwargs)

    def start(self, user):
        if self.admin.id == user.id and self.status is self.Status.OPEN and len(self.players) >= 2:
            self.status = self.Status.STARTED
            self.run()
        else:
            raise

    def run(self):
        self.deck = set(Card(self, suit, rank) for suit in range(1, 5) for rank in range(1, 14))
        for player in self.players:
            for _ in range(5):
                player.draw()
            player.show_hand()
        self.value = 0
        self.current = len(self.players) - 1
        self.direction = 1

    def draw(self):
        card = sample(self.deck, 1)[0]
        self.deck.remove(card)
        return card

    def next(self):
        if len(self.players) == 1:
            self.win()
            return
        self.show_value()
        self.current = (self.current + self.direction) % len(self.players)
        player = self.players[self.current]
        if player.is_available():
            self.send_message(Strings.TURN.format('@' + player.user.username), without = player)
            player.ask_discharge()
        else:
            player.burst()
            self.players.pop(self.current)
            if self.direction == 1:
                self.current -= 1
            self.next()

    def show_value(self):
        self.send_message(Strings.VALUE.format(str(self.value)))

    def discharge(self, user, idx):
        player = self.players[self.current]
        if player.user.id == user.id:
            if player.discharge(idx):
                self.next()
        else:
            raise

    def choose(self, user, idx):
        player = self.players[self.current]
        if player.user.id == user.id:
            player.choose(idx)
            self.next()
        else:
            raise

    def return_deck(self, card):
        self.deck.add(card)

    def win(self):
        self.players[0].win()
        self.status = self.Status.OFF
        self.players = []
