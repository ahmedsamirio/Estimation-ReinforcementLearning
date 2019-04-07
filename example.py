import env

env = env.Estimation()
obs, done, info = env.reset()
while True:
    print(info['current_player'], info['current_player_cards'])
    action = env.action_space.sample()
    obs, done, info = env.step(action)
    print(info['table'])
    if done:
        print(env.scores)
        break
