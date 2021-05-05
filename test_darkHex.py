from typing import Set
from game.darkHex import DarkHex
from agent.RandomAgent import RandomAgent
from agent.SetPolicyAgent import FixedPolicyAgent_wTree
import argparse

C_PLAYER1 = 'B'
C_PLAYER2 = 'W'

parser = argparse.ArgumentParser()
parser.add_argument("--verbose_white", "-vw", action="store_true", 
                    help="Turn on outputs for white player.", default=False)
args = parser.parse_args()

game = DarkHex(BOARD_SIZE=[3,4])
result = '='

actor1 = FixedPolicyAgent_wTree(C_PLAYER2, game.valid_moves)
actor2 = RandomAgent(C_PLAYER1)

i = 0
print('Player 1 (W) is played by the FixedPolicyAgent\n\
Player 2 (B) is you, please make a move according\n\
to the given table indexes. For 3x4 board here\n\
is the board indexes;\n\n\
 B   B   B   B \n\
 ---------------\n\
W\ 0   1   2   3  \W\n\
 W\ 4   5   6   7  \W\n\
  W\ 8   9   10  11 \W\n\
     ---------------\n\
       B   B   B   B' )
while result == '=':
    s = True
    if i % 2 == 0:
        result = 'f'
        if not args.verbose_white:
            game.verbose = False
        while result == 'f':
            action = actor1.step(observation=game.BOARDS[C_PLAYER2], success=s)
            board, done, result, reward = game.step(C_PLAYER2, action)
            s = False
        if args.verbose_white:    
            game.print_information_set(C_PLAYER2)
    else:
        result = 'f'
        game.verbose = True
        while result == 'f':
            try:
                action = int(input('move: ').strip())
                board, done, result, reward = game.step(C_PLAYER1, action)
            except KeyboardInterrupt:
                exit()
            except:
                print("Please enter a valid input, the format should be an int. i.e. 3")
                continue
        game.print_information_set(C_PLAYER1)
    i+=1
game.verbose = True
print('\nGame is over, the winner is:', game.game_status())
print('Here is the end game referee board:')
game.printBoard()
