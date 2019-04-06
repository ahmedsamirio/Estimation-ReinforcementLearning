# Estimation-ReinforcementLearning
An environment for training reinforcement learning algorithms on Estimation card game.

## Estimation Rules
Estimation is a game for 4 players in which the standard international 52-card pack is used. The game is normally played counter-clockwise. The objective of the game is for players to try to estimate the number of tricks they can get in each round.

### Cards and Dealing
13 cards are dealt to each player, the cards in each suit ranking from low to high: 2 - 3 - 4 - 5 - 6 - 7 - 8 - 9 - 10 - J - Q - K - A.

### Bidding
The bidding is split into two phases. In the first phase, players bid in turn according to the estimated number of tricks they think they can get, or declare a "Dash Call", which means that the estimated number of tricks is zero. Players have to declare their trump suit along with their bid. The winner of the bidding round is the player who estimates the highest number of tricks. In case of a tie, the trump suit is used to determine the winner. The suits are ranked from high to low: No Trump (NT), Spades, Hearts, Diamonds, Clubs.

After the winner is determined, players are given a chance to estimate the number of tricks they will get based on the trump suit that was selected. The maximum number of tricks a player can estimate is the number estimated by the winner of the bidding round.

### Play
The winner of the bidding round leads the first trick and players must follow suit. Each trick is won by the highest card and the winner of each trick leads the next.
Players unable to follow it have the option to use "trump" cards, which are considered the highest among other cards. The winner of the trick is the player who uses a trump, unless a higher trump is used.
The round ends when players are out of cards.
