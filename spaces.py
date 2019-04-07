import numpy as np
import random

class Action:
    """ 
    A class representing the action space
    """
    def __init__(self, env):
        self.n = 52
        self.env = env

    def sample(self):
        """
        A method which randomly samples a viable card from the current players hand and return card token
        """
        player = self.env.current_player()
        player_cards = self.env.players_cards[player]
        if self.env.table_suit:
            legal_cards = [card for card in player_cards if card[1] == self.env.table_suit]
            if not legal_cards:
                legal_cards = player_cards
        else:
            legal_cards = player_cards

        card = random.choice(legal_cards)

        if len(self.env.dash_players) == 2:
            call = np.random.randint(1, 14)
        else:
            call = np.random.choice(14)

        return [self.env.deck.card_to_token[card], call, np.random.choice(4)]



class Observation:
    """ 
    A class representing the observation space
    """
    def __init__(self, env, change_state_func):
        self.env = env
        self.change_state = change_state_func
        self.dim = self.change_state(self.env).shape

    def next(self):
        return self.change_state(self.env)



