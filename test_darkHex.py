from typing import Set
from game.darkHex import DarkHex
from agent.RandomAgent import RandomAgent
from agent.SetPolicyAgent import FixedPolicyAgent_wTree

game = DarkHex(BOARD_SIZE=[3,4])

# actor1 = RandomAgent('B')
actor1 = FixedPolicyAgent_wTree('W', game.valid_moves)
actor2 = RandomAgent('B')

i = 0
while game.check_game_status() == '=':
    s = True
    if i % 2 == 0:
        result = 'f'
        while result == 'f':
            action = actor1.step(observation=game.BOARDS['W'], success=s)
            board, done, result, reward = game.step('W', action)
            s = False
        game.printBoard_for_player('W')
    else:
        result = 'f'
        while result == 'f':
            try:
                action = list(map(int, (input('x y: ').strip().split(' '))))
                board, done, result, reward = game.step('B', action[::-1])
            except KeyboardInterrupt:
                exit()
            # except:
            #     print("Please enter a valid input, the format should be: int int")
            #     continue
        game.printBoard_for_player('B')
    print()
    # game.printBoard()
    i+=1

print('\nWinner:', game.check_game_status())
