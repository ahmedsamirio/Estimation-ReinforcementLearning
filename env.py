import numpy as np
import copy
from collections import defaultdict, Counter
from functions import *
from spaces import *

class Cards:
	"""
	A class representing a deck of cards
	"""
	def __init__(self):
		self.suits = ['C', 'D', 'H', 'S']
		self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
		self.cards = [(rank, suit) for suit in self.suits for rank in self.ranks]
		self.card_to_token = {card: i for i, card in enumerate(self.cards)}
		self.token_to_card = {i: card for i, card in enumerate(self.cards)}


	def shuffle(self):
		np.random.shuffle(self.cards) 


class Estimation:
	""" 
	A class representing a game of estimation
	"""
	def __init__(self, state_func=change_state, players=list('ABCD')):
		self.state_func = state_func
		self.players = players


	def reset(self):
		# game record
		self.record = {}

		# deck of cards
		self.deck = Cards()

		# players bids, tricks, score multipliers and scores
		self.bids = defaultdict(list)
		self.tricks = defaultdict(list)
		self.multi = defaultdict(list)
		self.scores = defaultdict(int)

		# each player's cards, table cards, previously played cards and total called tricks
		self.players_cards = defaultdict(list)
		self.table = []
		self.played = []
		self.total_tricks = 0


		# table suit and trump suit
		self.table_suit = ''
		self.trump_suit = ''

		# current player order, and round no.
		self.order = 0
		self.round = 0
		
		# initialize observation and action space
		self.observation_space = Observation(self, self.state_func)
		self.action_space = Action(self)


		# done flag, phase 1 flag, phase 2 flag and phase 3 flag
		self.done = False
		self.phase_1 = True
		self.phase_2 = False
		self.phase_3 = False
		self.dash = False
		self.dash_players = []

		# deal cards to players
		self.deal_to_players()

		# first player observation state
		self.state = self.observation_space.next()

		# return the observation state for the first player
		return self.state, self.update_info()

	
	def step(self, action):
		"""
		The action argument should be a list containing:
		1. a card to be played
		2. an estimation of tricks
		3. a trump suit
		"""

		# Phase 1
		if self.phase_1:
			# determine current player 
			player = self.current_player()

			# add the estimate and trump suit
			self.bid(player, action)

			if self.order < 3:  # if still in the bidding phase
				self.order += 1 
			
			else:  # if the bidding phase is over
				self.select_highest_bid()
				self.record['bids'] = self.bids

				# update flags
				self.phase_1 = False
				self.phase_2 = True

			self.state = self.observation_space.next()
			info = self.update_info()

			return self.state, self.done, info

		# Phase 2
		elif self.phase_2:
			# determine current player
			player = self.current_player()

			# if not the last player
			if self.order < self.last_player:
				self.call(player, action)
				self.order += 1
				if self.dash:
					if self.order == self.dash_skip:
						self.order += 1
			else:
				self.call(player, action, last_player=True)
				self.order = 0 

				# update flags
				self.phase_2 = False
				self.phase_3 = True

			self.state = self.observation_space.next()
			info = self.update_info()

			return self.state, self.done, info

		# Phase 3
		elif self.phase_3:
			player = self.current_player()
			self.play_card(player, action)
			self.order += 1  # set up the order for the next player
			if self.order > 3:
				self.order = 0
				self.round += 1
				winner = self.evaulate_winner()

				self.assign_tricks(winner)
				self.update_record()
				self.reorder_players(winner)
				self.empty_table()

			if self.round == 13:
				self.done = True
				self.post_game_multi()
				self.update_scores()
				self.record['scores'] = self.scores  # add the final score the game record

			self.state = self.observation_space.next()
			info = self.update_info()

			return self.state, self.done, info 


	def select_highest_bid(self):
		"""
		A method which determines the highest bidding player and reorder the players accordingly
		"""
		max_trump = 0
		max_est = 0
		
		# loop over players bids
		for player, bid in self.bids.items():
			# if a player dashed
			if bid[0] == 0:
				# if this was the first player to dash
				if not self.dash:
					self.multi[player].append('dash')
					self.dash = True  # initialize a dash flag 
					self.dash_players = list(player)
				elif self.dash and len(self.dash_players) < 2:
					self.multi[player].append('dash')
					self.dash_players.append(player)

			# if the player estimation exceeded the max one
			elif bid[0] > max_est:
				max_est = bid[0]
				max_trump = bid[1]
				highest_player = player
			# if the player estimation equaled the max one
			elif bid[0] == max_est:
				# if the trump suit was of greater value than the previous one
				if bid[1] > max_trump:
					max_est = bid[0]
					max_trump = bid[1]
					highest_player = player
			

		self.multi[highest_player].append('bidder')  # append bidder multiplier for score calculation
		self.bids[highest_player] = max_est  # change the bid value to contain only the estimated tricks
		self.highest_bid = max_est
		self.trump_suit = self.deck.suits[max_trump]  # set the trump suit
		self.record['trump_suit'] = self.deck.suits[max_trump]
		self.total_tricks += max_est

		# reorder players and reintialize other players' bids for phase 2
		self.reorder_players(highest_player)
		self.reinitialize_bids(highest_player)
		self.last_player = 3
		self.order = 1

		# reinitialize order to start phase 2
		if self.dash:
			if len(self.dash_players) == 1:
				dash_player_order = self.players.index(self.dash_players[0])
				if dash_player_order == 1:
					self.order = 2
					self.dash_skip = 1
					self.last_player = 3
				elif dash_player_order == 2:
					self.order = 1
					self.dash_skip = 2
					self.last_player = 3
				elif dash_player_order == 3:
					self.last_player = 2
			else:
				dash_players_order = set([self.players.index(player) for player in self.dash_players])
				players_order = set([1, 2, 3])
				self.last_player = players_order.difference(dash_players_order).pop()
				self.order = self.last_player

	def reorder_players(self, winner):
		"""
		A method which reorder players according to the round winner
		"""
		winner_order = self.players.index(winner)
		for _ in range(winner_order):
			self.players.insert(3, self.players.pop(0))




	def reinitialize_bids(self, highest_player):
		"""
		A method which reinitializes bid for players who didn't win in the bidding phase
		"""
		for player in self.players:
			if player is not highest_player:
				self.bids[player] = 0


	def deal_to_players(self):
		# shuffle the deck
		self.deck.shuffle()

		# give each player 13 cards
		for _ in range(13):
			for player in self.players:
				self.players_cards[player].append(self.deck.cards.pop())

	def update_info(self):
		"""
		A method which returns a dict containing keys:
			1. round
			2. current_player
			3. players_order
			4. players_cards: a dict containing the current hand of each player
			5. players_bids: a dict containing the bids of each player
			6. players_tricks: a dict containing the tricks of each player
			7. table: a list of cards on the table
			8. table_suit
			9. trump_suit
			8. played_cards: a list of played cards
			9. scores

			In case this was the last player's call, a flag will be included with a illegal estimation number
		"""
		info = {}
		info['round'] = self.round
		info['current_player'] = self.current_player()
		info['current_player_cards'] = self.players_cards[self.current_player()]
		info['player_order'] = self.players
		info['players_cards'] = self.players_cards
		info['players_bids'] = self.bids
		info['players_tricks'] = self.tricks
		info['table'] = self.table
		info['table_suit'] = self.table_suit
		info['trump_suit'] = self.trump_suit
		info['played_cards'] = self.played
		info['scores'] = self.scores

		if self.phase_2 and self.current_player() is self.last_player:
			info['last_call'] = True
			info['illegal_call'] = 13 - self.total_tricks


		if self.phase_1:
			bids = [bid[0] for bid in self.bids.values() if bid]
			if Counter(bids)[0] > 1:
				info['illegal_call'] = 0

		return info

	def update_record(self):
		"""
		A method which update the record dict of the game with info about recent round
		"""
		info = {}
		info['players_order'] = copy.deepcopy(self.players)
		info['players_cards'] = copy.deepcopy(self.players_cards)
		info['players_tricks'] = copy.deepcopy(self.tricks)
		info['table'] = copy.deepcopy(self.table)
		info['table_suit'] = copy.deepcopy(self.table_suit)

		self.record[self.round] = info

	def current_player(self):
		"""
		A method to determine the current player
		"""
		return self.players[self.order]

	def bid(self, player, action):
		"""
		A method to add bid for a player in phase 1
		"""
		self.bids[player].extend(action[1:])

	def call(self, player, action, last_player=False):
		"""
		A method which takes an estimation from players in phase 2 and adds score multipliers
		"""
		call = action[1]
		if not last_player:
			if call == self.highest_bid:
				self.multi[player].append('with')
		else:
			if call == self.highest_bid:
				if call + self.total_tricks == 15:
					self.multi[player].append('withrisk')
				elif call + self.total_tricks > 15:
			 		self.multi[player].append('withdoublerisk')
				else:
			  		self.multi[player].append('with')

			elif call != 0:
				if call + self.total_tricks == 15:
					self.multi[player].append('risk')
				elif call + self.total_tricks > 15:
					self.multi[player].append('doublerisk')
				else:
					self.multi[player].append('regular')

		if call == 0:
			self.multi[player].append('nocall')

		elif call >= 8:
			self.multi[player].append('>=8')

		self.bids[player] = call
		self.total_tricks += call

	def play_card(self, player, action):
		"""
		A method to player a card through a given action
		"""
		hand = self.players_cards[player]
		card_token = action[0]  
		card = self.deck.token_to_card[card_token]
		card_index =  hand.index(card)  # index of the card in players hand
		self.table.append(hand.pop(card_index))  # add the card to the table
		
		# declare table suit if it was the first card on the table
		if len(self.table) == 1:
			self.table_suit = card[1]

	def evaulate_winner(self):
		"""
		A method to evaluate winner
		"""
		if self.check_trump():
			# filter the cards to only include trump cards if a trump card was played
		    cards = [self.deck.card_to_token[card] if card[-1] == self.trump_suit else 0 for card in self.table]
		else:
			# filter the cards to only include cards of the table suit
		    cards = [self.deck.card_to_token[card] if card[-1] == self.table_suit else 0 for card in self.table]

		# returns the player with the highest card value
		return self.players[np.argmax(cards)]

	def check_trump(self):
		"""
		A method to check whether the table cards contain trump cards
		"""
		suits = [card[-1] for card in self.table]
		if self.trump_suit in suits:
		    return True
		else:
		    return False

	def assign_tricks(self, winner):
		"""
		A method which assigns tricks after a succesful round
		"""
		for player in self.players:
			if player is winner:
				self.tricks[player].append(1)
			else:
				self.tricks[player].append(0)

	def empty_table(self):
		"""
		A method which empties a table after a mini round and resets table suit
		"""
		for _ in range(4):
			self.played.append(self.table.pop())

		self.table_suit = ''

	def post_game_multi(self):
		"""
		A method which for post game score multiplier determination
		"""
		outcomes = {}
		for player in self.players:
			if self.bids[player] == sum(self.tricks[player]):
				outcomes[player] = 1
			else:
				outcomes[player] = 0
		wins = sum(outcomes.values())
		if wins == 1:
			for player, outcome in outcomes.items():
				if outcome == 1:
					self.multi[player].append('onlywin')
			if wins == 3:
				for player, outcome in outcomes.items():
					if outcome == 0:
						self.multi[player].append('onlylose')

	def update_scores(self):
		"""
		A method which updates scores after the end of the game according to tricks and multipliers
    	"""

		X = np.zeros(4)  # main points
		Y = np.zeros(4)  # extra points
		Z = np.ones(4)  # bidding multipliers
		won = False


		for i, player in enumerate(self.players):  # Main points
			player_estimated = self.bids[player]
			player_actual = sum(self.tricks[player])
			if player_actual == player_estimated:
				X[i] += player_estimated
				won = True
			else:
				X[i] -= abs(player_estimated - player_actual)
				won = False

			if 'bidder' in self.multi[player]:
				if won:
					Y[i] += 20
				else:
					Y[i] -= 10

			if 'dash' in self.multi[player]:
				if won:
					Y[i] += 23
				else:
					Y[i] -= 23

			if 'regular' in self.multi[player]:
				if won:
					Y[i] += 10

			if 'risk' in self.multi[player]:
				if won:
					Y[i] += 20
				else:
					Y[i] -= 10

			if 'doublerisk' in self.multi[player]:
				if won:
					Y[i] += 30
				else:
					Y[i] -= 20

			if 'with' in self.multi[player]:
				if won:
					Y[i] += 20
				else:
					Y[i] -= 10

			if 'withrisk' in self.multi[player]:
				if won:
					self.scores[i] += 30
				else:
					self.scores[i] -= 20

			if 'withdoublerisk' in self.multi[player]:
				if won:
					Y[i] += 40
				else:
					Y[i] -= 30

			if 'onlywin' in self.multi[player]:
				Y[i] += 10

			if 'onlylose' in self.multi[player]:
				Y[i] -= 10

			if 'nocall' in self.multi[player]:
				if won:
					Y[i] += 10
				else:
					Y[i] -= 10

			if '>=8' in self.multi[player]:
				Z[i] = 2

		scores = (X + Y) * Z + (X + Y) * (Z - 1)
		for i, score in enumerate(scores):
			player = self.players[i]
			self.scores[player] = score


