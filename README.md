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

More information about scoring can be found here: https://www.jawaker.com/en/rules/estimation

## Installation
```git clone https://github.com/ahmedsamirio/Estimation-ReinforcementLearning.git```

## Usage
The environment was designed to be as close to OpenAI gym as possible. Each simulation will be just one round of a full game, ending with a calculation of scores.
```
import env
env = env.Estimation()
obs, info = env.reset()
while True:
    action = env.action_space.sample()
    obs, rewards, done, info = env.step(action)
    
    if done:
        print(env.scores)
        break
```

To know what's happening in the game, the info dict is provided. It contains information about:
   
1. The current player ```current_player``` 
2. The current player cards ```current_player_cards```
3. The order of the players ```player_order```
4. The cards of all player ```players_cards``` this will be dictionary
5. The players' bids ```players_bids```  
6. The cards on the table ```table```    
7. The suit of the table ```table_suit``` 
8. The trump suit ```trump_suit``` 
9. The played cards ```played_cards``` 
10. The scores ```scores``` which are only updated at the end


Through this info dict, you are able to handcraft the observation the way you want and not stick to the observation supplied by the environment. 

Alternatively, you can pass the instance a function that return the current environment state based on it's attributes. For example, you can take a look at the default function ```change_state``` at [`functions.py`](./functions.py)



This function is elementary, and other functions can be used to make more meaningful represenations of the current state of the environment using other techniques.

The main attributes that you'd want to be using in making a state representation are:
1. The current player's cards  ```self.players_cards[self.current_player()]``` 
2. Cards on the table if any  ```self.table```
3. Previously played cards if any  ```self.played_cards```
4. The current player's bids and collected tricks  ```self.bids[self.current_player()]``` ```self.tricks[self.current_player()]```
5. Other players' bids and collected tricks  ```self.bids``` ```self.tricks```
6. Table and trump suits  ```self.table_suit``` ```self.trump_suit```
7. The total asked tricks from all players  ```self.tricks```
8. The round no.  ```self.round```
9. The current player order on the table  ```self.order```

## Caveats about the environment

### Players

You can provide two arguments while calling an instance of the environment. The first one is the state function responsible for crafting the current player's state, and a list of players.

The default list supplied is ```['A', 'B', 'C', 'D']```. This is totally optional and you can change it however you like. You can also use multiple neural networks, or only one network for all players. For example:
```
players = {'Bob': Net(), 'Dick': Net(), 'Gabe': Net(), 'Elmo': Net()}
env = env.Estimation(players=players.keys())
obs, info = env.reset()
while True:
    player = info['current_player']
    action = players[player](obs)
    action = process_action(action)
    action = policy(action)
    obs, rewards, done, info = env.step(action)
    if done:
        break
```     

Or
```
players = ['Bob', 'Dick', 'Gabe', 'Elmo']
env = env.Estimation(players=players)
net = Net()
obs, info = env.reset()
while True:
    action = net(obs)
    action = process_action(action)
    action = policy(action)
    obs, rewards, done, info = env.step(action)
    if done:
        break
```

### Actions

For simplicity, all actions passed to the environment should be tuples of 3 elements. The first element should be the card token, the second is the estimation, and the third is the trump suit token. 

During the first phase, the 2nd and 3rd element are used. The second phase will only use the 2nd element, and the 3rd will use the first. 



### Bids 

During the first phase, the bids dictionary will contain (estimation, trump_token) tuples for each player. Therefore you should be wary while using it in the state representation. Hence why this line existed in the state function:

```state[52] = env.bids[player] if not isinstance(env.bids[player], list) else 0```

During the second phase, the bids dictionary will only contain the estimation number.

For the sake of brevity let's call the first phase bidding, and the second calling. 

During calling, the last player isn't allowed to call a number that makes the total tricks equal 13, and so the info dictionary will contain a key with a flag only in the case that the current player is the last player in calling, and will contain a key supplying the illegal estimation. 

You can then tweak the function which return the estimation based on the neural network output, for example, to return only a call from the legal ones.

### Tricks

The tricks are recorded for each player as 0 or 1 in a each round, so the ```self.tricks``` dict will contain lists. This has the advantage of letting you calculate the correct amount of tricks collected after each time step, providing more training data for calculation estimtaions.

The function ```collective_estimation_calculation``` takes the ```self.tricks``` dict, and return another dict with the tricks collected after each step for each player.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
