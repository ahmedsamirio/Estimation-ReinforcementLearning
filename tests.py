from env import *

env = Estimation(change_state, list('ABCD'))
obs, done, info = env.reset()
while True:
    print(info['current_player'], info['current_player_cards'])
    action = env.action_space.sample()
    obs, done, info = env.step(action)
    print(info['table'])

    if done:
        print(env.record['scores'])
        print(env.record[2])
        break

