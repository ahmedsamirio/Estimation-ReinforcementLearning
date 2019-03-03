import numpy as np

class Player:
    """ A class representing a player """
    def __init__(self, name, deck):
        self.hand = []
        self.avoid = False
        self.name = name
        self.suit_ranks = deck.suits
        self.dash = None # Flag to determine if the players dashed
        self.won = None # Flag to determine if player one or lost

    # a method to show a player's hand
    def show_hand(self):
        print(self.hand)

    # a method for choosing player's bid
    def bid(self, max_suit='C', max_no=0):
        if input('Dash? (y/n)\n') == 'y':
            self.dash = True
            return None
        self.bid_no = int(input('Enter no. of tricks\n'))
        self.bid_suit = input('Enter suit\n')
        if self.bid_no > max_no and self.suit_ranks.index(self.bid_suit) >= self.suit_ranks.index(max_suit):
            return (self.name, self.bid_suit, self.bid_no)

        return None

    # a method for choosing player's call
    def call(self, trump_suit, forbidden=None):
        self.bid_no = int(input('Enter no. of tricks'))
        while self.bid_no == forbidden:
            self.bid_no = int(input('Bid can\'t be equal to {}'.format(forbidden)))

        self.trump_suit = trump_suit
        return self.bid_no

    # a method for checking the presence of all suits in player's hand
    def check_avoid(self):
        suits = [card[0] for card in self.hand]
        if len(np.unique(suits)) < 4:
            self.avoid = True

    # a method for asking player to continue to reset round if he's avoid
    def player_choice(self):
        choice = input('Continue? (y/n)')
        if choice == 'y':
            return True
        else:
            return False

    def play(self):
        pass
