from player import Player
from deck import Deck
from scoreboard import Scoreboard
import numpy as np


class Game:
    """ A class representing a full estimation game """

    def __init__(self):
        self.deck = Deck()
        self.players = [Player(name, self.deck) for name in 'ABCD']
        self.players_orders = {player: index for index, player in enumerate(self.players)}
        self.scoreboard = Scoreboard()

    def start_game(self):
        for _ in range(18):
            self.reset()
            self.round.deal_to_players()
            self.round.bidding()
            self.round.play()
            self.round.post_round_multi()
            self.scoreboard.update_scores(self.round.bids, self.round.tricks, self.round.multi, self.players_orders,
                                          self.round.saydah)

    def reset(self):
        self.round = Round(self.players, self.deck)


class Round:
    """ A class representing a round of estimation card game """

    def __init__(self, players, deck):
        self.deck = deck
        self.players = players
        self.trump_suit = ''  # To be decided during bidding
        self.highest_bid = 0 # To be decided during bidding
        self.bids = {}  # maps each player to his expected bids
        self.tricks = {player: 0 for player in self.players}  # maps each players to his recorded tricks
        self.multi = self.multi = {player: [] for player in self.players}  # maps each players to a list of multipliers
        self.scoreboard = Scoreboard()
        self.saydah = False

    # a method to deal to players
    def deal_to_players(self):
        self.deck.shuffle()
        for _ in range(13):
            for player in self.players:
                card = self.deck.deal_card()
                player.hand.append(card)
        for player in self.players:  # check that all players have all suits
            player.check_avoid()
            if player.avoid:  # if a player avoided a suit
                if player.player_choice():
                    pass
                else:
                    self.deal_to_players()

    # a method which starts bidding in the beginning of the round
    def bidding(self):
        max_suit = 'C'  # record the lowest suit
        max_no = 0  # record the lowest bid no.
        for player in self.players:  # loop over players to find the highest bid
            bid = player.bid(max_suit, max_no)  # if the bid didn't exceed the max it bid = None
            if player.dash:
                self.multi[player].append('dash')  # add dash multiplier to players who dashed
            if bid:
                self.highest_bid = [player, bid[1], bid[2]]
                max_suit = bid[1]
                max_no = bid[2]
        highest_player_index = self.players.index(self.highest_bid[0])
        self.multi[self.players[highest_player_index]].append('bidder')  # multiplier to player with highest bid
        self.trump_suit = self.highest_bid[1]
        # TODO Need to add a way to include null trump suit when making the neural networks
        for _ in range(highest_player_index):  # reorder the players so that the highest bidder starts first
            self.players.insert(3, self.players.pop(0))

        total_tricks = self.highest_bid[2]
        self.bids[self.players[0]] = self.highest_bid[2]
        for player in self.players[1:]:
            if self.players.index(player) == 3:
                forbidden = 13 - total_tricks
                bid = player.call(self.trump_suit, forbidden)
                if bid == self.highest_bid[2]:
                    if bid + total_tricks == 15:
                        self.multi[player].append('withrisk')
                    elif bid + total_tricks > 15:
                        self.multi[player].append('withdoublerisk')
                    else:
                        self.multi[player].append('with')

                elif bid != 0:
                    if bid + total_tricks == 15:
                        self.multi[player].append('risk')
                    elif bid + total_tricks > 15:
                        self.multi[player].append('doublerisk')
                    else:
                        self.multi[player].append('regular')

                elif bid == 0:
                    self.multi[player].append('nocall')

                if bid >= 8:
                    self.multi[player].append('>=8')

            else:
                bid = player.call(self.trump_suit)
                if bid == self.highest_bid[2]:
                    self.multi[player].append('with')
            self.bids[player] = bid
            total_tricks += bid

    def show_players(self):
        print(self.players)

    def post_round_multi(self):
        wins = 0
        for player in self.players:
            estimated = self.bids[player]
            collected = self.tricks[player]
            if estimated == collected:
                player.won = True
                wins += 1
        if wins == 3:
            for player in self.players:
                self.multi[player].append('onlylose') if not player.won
        elif wins == 1:
            for player in self.players:
                self.multi[player].append('onlywin') if player.won



    def play(self):
        # Simple for loops for each 13 mini-rounds with nested for loop to get the card from each player then
        # determining the winning player
        for _ in range(13):
            cards = []
            for player in self.players:
                card = player.play()
                cards.append(card)
            cards = self.deck.convert_indices(cards)
            trump_cards = self.deck.trump_indices(self.trump_suit)
            if trump_suit:
                cards = [card if card in trump_cards else 0  for card in cards]
            winning_player = self.players[np.argmax(cards)]
            self.tricks[winning_player] += 1
