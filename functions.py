import numpy as np

def change_state(env):
    """
    A function which return the observation state of the current player
    The first 52 elements [0:52] are label encodings of the cards:
        a) 0 - the card isn't played yet and isn't in hand
        b) 1 - the card is in hand
        c) 2 - the card is on the table
        d) 3 - the card has been played before

    The next 8 elements [52:60] contain information about the bids and tricks
        a) [52:54] - contains info about current player bids and tricks
        b) [54:60] - contains info about other 3 players

    The elements in [60:62] contain the table and trump suits label encodings
        a) 0 encodes clubs
        b) 1 encodes diamonds
        c) 2 encodes hearts
        d) 3 encodes spades
        e) 4 encodes no suit

    The last three elements [62:64] encode the total asked tricks, round no. and current player order
    """

    player = env.current_player()
    player_cards = env.players_cards[player]
    player_cards_tokens = [env.deck.card_to_token[card] for card in player_cards]
    state = np.zeros(65,)
    for token in player_cards_tokens:
        state[token] = 1
    # if there are cards on the table
    if env.table:
        table_tokens = [env.deck.card_to_token[card] for card in env.table]
        for token in table_tokens:
            state[token] = 2
    # if there are played cards
    if env.played:
        played_tokens = [env.deck.card_to_token[card] for card in env.played]
        for token in played_tokens:
            state[token] = 3
    
    other_players = env.players[:]
    other_players.remove(player)

    # if players finished the first and/or the second phase
    if env.bids:
        state[52] = env.bids[player] if not isinstance(env.bids[player], list) else 0
        for i, p in enumerate(other_players):
            state[54+(i*2)] = env.bids[p] if not isinstance(env.bids[player], list) else 0
    # if players collected any tricks
    if env.tricks:
        state[53] = sum(env.tricks[player])
        for i, p in enumerate(other_players):
            state[55+(i*2)] = sum(env.tricks[p])

    # if there is a table suit
    if env.table_suit:
        state[60] = env.deck.suits.index(env.table_suit)
    else:
        state[60] = 4
    
    # if there is a trump suit
    if env.trump_suit:
        state[61] = env.deck.suits.index(env.trump_suit)
    else:
        state[61] = 4

    # total asked tricks, round no. and current player order
    state[62] = env.total_tricks
    state[63] = env.round
    state[64] = env.order

    return state




def filter_legal_cards(card_probs, env):
    """
    A function which filters out values of cards or probabilities to the legal ones only
    """
    player = env.current_player()
    player_cards = env.players_cards[player]
    if env.table_suit:
        legal_cards = [card for card in player_cards if card[1] == env.table_suit]
        if not legal_cards:
            legal_cards = player_cards
    else:
        legal_cards = player_cards
    cards_tokens = [env.deck.card_to_token[card] for card in legal_cards]
    
	# filter card probabilties by their presence in the legal card tokens
    legal_card_probs = [prob if i in cards_tokens else 0 for i, prob in enumerate(card_probs)]

	# in case the probability of the last card was zero
    if sum(legal_card_probs) == 0:
        for i, x in enumerate(legal_card_probs):
            if isinstance(x, float):
                legal_card_probs[i] = 1.0

    return legal_card_probs


def filter_legal_calls(call_probs, info):
	"""
	A function which filters out legal calls
	"""
	if 'illegal_call' in info.keys():
		call_probs = [prob if i != info['illegal_call'] else 0 for i, prob in enumerate(call_probs)]
		print(call_probs)
	
	return call_probs


def process_action(action, env, info):
	"""
	A function which filter out the legal actions
	"""
	card_probs, call_probs, trump_probs = action
	legal_card_probs = filter_legal_cards(card_probs, env)
	legal_call_probs = filter_legal_calls(call_probs, info)
	
	return [legal_card_probs, legal_call_probs, trump_probs]

def norm(arr):
	return arr/sum(arr)


def calculate_estimations_over_steps(tricks):
    """
    A function which calculate the tricks collected after each step in the game for a player
    """
    correct_estimations = []  # a list of tricks collected after each step
    for i in range(13):
        correct_estimations.append(abs(np.sum(tricks[i:])))

    return correct_estimations

def collective_estimation_calculation(env):
    """
    A function which calculates the tricks collected after each step in the game for all players
    """
    correct_estimations = {}
    for player, tricks in env.tricks.items():
        correct_estimations[player] = calculate_estimations_over_steps(tricks)

    return correct_estimations
