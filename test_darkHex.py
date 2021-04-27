from typing import Set
from game.darkHex import DarkHex
from agent.RandomAgent import RandomAgent
from agent.SetPolicyAgent import FixedPolicyAgent_wTree

game = DarkHex(BOARD_SIZE=[3,4])
done = False

# actor1 = RandomAgent('B')
actor1 = FixedPolicyAgent_wTree('W', game.valid_moves)
actor2 = RandomAgent('B')

i = 0
print('Player 1 (W) is played by the FixedPolicyAgent\n\
Player 2 (B) is you, please make a move according\n\
to the given table indexes. For 3x4 board here\n\
is the board indexes;\n\n\
0   1   2   3 \n\
  4   5   6   7 \n\
    8   9   10  11')
while not done:
    s = True
    if i % 2 == 0:
        result = 'f'
        game.verbose = False
        while result == 'f':
            action = actor1.step(observation=game.BOARDS['W'], success=s)
            board, done, result, reward = game.step('W', action)
            s = False
        # game.printBoard_for_player('W')
    else:
        result = 'f'
        game.verbose = True
        while result == 'f':
            try:
                action = int(input('move: ').strip())
                board, done, result, reward = game.step('B', action)
            except KeyboardInterrupt:
                exit()
            except:
                print("Please enter a valid input, the format should be an int. i.e. 3")
                continue
        game.printBoard_for_player('B')
    # game.printBoard()
    i+=1

print('\nWinner:', game.game_status())
