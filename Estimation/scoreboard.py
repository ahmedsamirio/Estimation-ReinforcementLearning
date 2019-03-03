import numpy as np

class Scoreboard:
    """ A simple representation of an estimation scoreboard """

    def __init__(self):
        self.scores = np.zeros((1, 4))


    def update_scores(self, estimated, actual, multi, order, saydah=False):
        X = np.zeros((1, 4)) # main points
        Y = np.zeros((1, 4)) # extra points
        Z = np.ones((1, 4)) # bidding multipliers
        W = 2 if saydah else 1 # Sa'ydah multiplier

        for player, idx in order.items(): # Main points
            player_estimated = estimated[player]
            player_actual = actual[player]
            if player_actual == player_estimated:
                X[idx] += player_estimated
                player.won = True
            else:
                X[idx] -= abs(player_estimated - player_actual)
                player.won = False

            if 'bidder' in multi[player]:
                if player.won:
                    Y[idx] += 20
                else:
                    Y[idx] -= 10

            if 'dash' in multi[player]:
                if player.won:
                    Y[idx] += 23
                else:
                    Y[idx] -= 23

            if 'regular' in multi[player]:
                if player.won:
                    Y[idx] += 10

            if 'risk' in multi[player]:
                if player.won:
                    Y[idx] += 20
                else:
                    Y[idx] -= 10

            if 'doublerisk' in multi[player]:
                if player.won:
                    Y[idx] += 30
                else:
                    Y[idx] -= 20

            if 'with' in multi[player]:
                if player.won:
                    Y[idx] += 20
                else:
                    Y[idx] -= 10

            if 'withrisk' in multi[player]:
                if player.won:
                    self.scores[idx] += 30
                else:
                    self.scores[idx] -= 20

            if 'withdoublerisk' in multi[player]:
                if player.won:
                    Y[idx] += 40
                else:
                    Y[idx] -= 30

            if 'onlywin' in multi[player]:
                Y[idx] += 10

            if 'onlylose' in multi[player]:
                Y[idx] -= 10

            if 'nocall' in multi[player]:
                if player.won:
                    Y[idx] += 10
                else:
                    Y[idx] -= 10

            if '>=8' in multi[player]:
                Z[idx] = 2

        final_scores = (X + Y) * Z + (X + Y) * (W - 1) + (X + Y) * (Z - 1) * (W - 1)
        self.scores += final_scores

