import random

class Deck:
    """ A class representing a deck of 52 cards """
    def __init__(self):
        self.suits = ['C', 'D', 'H', 'S']
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.new_deck()
        self.indices = {card: i for i, card in enumerate(self.cards)}

    # a method to shuffle the deck
    def shuffle(self):
        random.shuffle(self.cards)

    # a method to deal cards to each player on at a time
    def deal_card(self):
        return self.cards.pop()

    # a mehod to show the deck
    def show_deck(self):
        print(self.cards)

    # a method to reset the deck
    def new_deck(self):
        self.cards = [rank + suit for suit in self.suits for rank in self.ranks]

    def convert_indices(self, cards):
        return [self.indices[card] for card in cards]
