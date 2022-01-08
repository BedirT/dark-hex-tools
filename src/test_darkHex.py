from Projects.base.game.darkHex import DarkHex
from Projects.base.game.hex import print_init_board, pieces
from Projects.base.agent.RandomAgent import RandomAgent
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--verbose_player", "-vp", action="store_true", 
                    help="Turn on outputs for the Fixed Policy player.", default=False)
args = parser.parse_args()
actor1 = RandomAgent(pieces.kBlack)
actor2 = RandomAgent(pieces.kWhite)
# print('Player 1 (W) is played by the FixedPolicyAgent\n\
# Player 2 (B) is you, please make a move according\n\
# to the given table indexes. For 3x4 board here\n\
# is the board indexes;\n')
# print_init_board(num_cols=game.num_cols, num_rows=game.num_rows)

# count winners
counter = {pieces.kBlack: 0, pieces.kWhite: 0}
num_iterations = 100000
for i in range(num_iterations):
    game = DarkHex(BOARD_SIZE=[3,4], verbose=False)
    result = pieces.kDraw
    i = 0
    while result == pieces.kDraw:
        result = pieces.kFail
        if i % 2 == 0:
            while result == pieces.kFail:
                action = actor1.step(game.BOARDS[pieces.kWhite])
                board, result, reward = game.step(pieces.kWhite, action)
        else:
            while result == pieces.kFail:
                action = actor2.step(game.BOARDS[pieces.kBlack])
                board, result, reward = game.step(pieces.kBlack, action)
        i+=1
    if result == pieces.kBlack:
        counter[pieces.kBlack] += 1
    elif result == pieces.kWhite:
        counter[pieces.kWhite] += 1
# report winners
print(f'Player 1 (W) wins: {counter[pieces.kBlack]}')
print(f'Player 2 (B) wins: {counter[pieces.kWhite]}')