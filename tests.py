import unittest
from env import Estimation

class TestEstimation(unittest.TestCase):
    """
    Test for class Estimation
    """

    def test_select_highest_bid(self):
        
        # test bidding 
        env = Estimation()
        _, _, _ = env.reset()
        
        env.bids['A'] = (5, 1)
        env.bids['B'] = (4, 3)
        env.bids['C'] = (6, 2)
        env.bids['D'] = (5, 3)

        env.select_highest_bid()
        self.assertEqual(env.players, ['C', 'D', 'A', 'B'])
        self.assertEqual(env.multi['C'], ['bidder'])
        self.assertEqual(env.highest_bid, 6)
        self.assertEqual(env.trump_suit, 'H')
        self.assertEqual(env.total_tricks, 6)

        # test bidding with dash call
        env = Estimation()
        _, _, _ = env.reset()
        

        env.bids['A'] = (0, 1)
        env.bids['B'] = (4, 3)
        env.bids['C'] = (6, 2)
        env.bids['D'] = (5, 3)
        env.select_highest_bid()
        self.assertEqual(env.players, ['C', 'D', 'A', 'B'])
        self.assertEqual(env.multi['C'], ['bidder'])
        self.assertEqual(env.highest_bid, 6)
        self.assertEqual(env.trump_suit, 'H')
        self.assertEqual(env.total_tricks, 6)
        self.assertIn('dash', env.multi['A'])
        self.assertTrue(env.dash)


    def test_reorder_players(self):
        env = Estimation()
        _, _, _ = env.reset()
        
        env.reorder_players('D')
        self.assertEqual(env.players, list('DABC'))

        env.reorder_players('A')
        self.assertEqual(env.players, list('ABCD'))

        env.reorder_players('C')
        self.assertEqual(env.players, list('CDAB'))

        env.reorder_players('B')
        self.assertEqual(env.players, list('BCDA'))

    def test_deal_to_players(self):
        env = Estimation()
        _, _, _ = env.reset()
        self.assertEqual(len(env.players_cards['A']), 13)
        self.assertEqual(len(env.players_cards['B']), 13)
        self.assertEqual(len(env.players_cards['C']), 13)
        self.assertEqual(len(env.players_cards['D']), 13)

        self.assertFalse(set(env.players_cards['A']).issubset(set(env.players_cards['B'])))
        self.assertFalse(set(env.players_cards['A']).issubset(set(env.players_cards['C'])))
        self.assertFalse(set(env.players_cards['A']).issubset(set(env.players_cards['D'])))
        self.assertFalse(set(env.players_cards['B']).issubset(set(env.players_cards['C'])))
        self.assertFalse(set(env.players_cards['B']).issubset(set(env.players_cards['D'])))
        self.assertFalse(set(env.players_cards['C']).issubset(set(env.players_cards['D'])))

    def test_current_player(self):
        env = Estimation()
        _, _, _ = env.reset()
        self.assertEqual(env.current_player(), 'A')

    def test_bid(self):
        env = Estimation()
        _, _, _ = env.reset()

        env.bid('A', (14, 6, 2))
        self.assertEqual(env.bids['A'], [6, 2])

    def test_call(self):
        env = Estimation()
        _, _, _ = env.reset()
        env.highest_bid = 6
        env.total_tricks = 10
        env.call('C', (51, 6, 3), last_player=True)
        self.assertIn('withdoublerisk', env.multi['C'])

        env = Estimation()
        _, _, _ = env.reset()
        env.highest_bid = 6
        env.total_tricks = 10
        env.call('C', (51, 5, 3), last_player=True)
        self.assertIn('risk', env.multi['C'])

        env = Estimation()
        _, _, _ = env.reset()
        env.highest_bid = 6
        env.total_tricks = 10
        env.call('C', (51, 8, 3))
        self.assertIn('>=8', env.multi['C'])

        env = Estimation()
        _, _, _ = env.reset()
        env.phase_2 = True
        env.last_player = 'D'
        env.order = 3
        env.total_tricks = 10
        info = env.update_info()
        self.assertTrue(info['last_call'])
        self.assertEqual(info['illegal_call'], 3)



unittest.main()

