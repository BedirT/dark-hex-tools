from typing import Set
from game.darkHex import DarkHex
from agent.RandomAgent import RandomAgent
from agent.SetPolicyAgent import FixedPolicyAgent

game = DarkHex()

# actor1 = RandomAgent('B')
actor1 = FixedPolicyAgent('B')
actor2 = RandomAgent('W')

i = 0
h = [] # history
while game.check_game_status() == '=':
    if i % 2 == 0:
        result = 'f'
        while result == 'f':
            action = actor1.step(round=i//2, history=h)
            board, done, result, reward = game.step('B', action)
        game.printBoard_for_player('B')
    else:
        result = 'f'
        while result == 'f':
            # action = actor2.step(game.BOARD)
            action = list(map(int, (input('x y: ').split(' '))))
            board, done, result, reward = game.step('W', action)
        game.printBoard_for_player('W')
    h.append(action)
    print()
    # game.printBoard()
    i+=1

print('\nWinner:', game.check_game_status())
