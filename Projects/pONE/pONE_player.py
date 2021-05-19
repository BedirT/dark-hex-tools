# loads pickle data on given path
import pickle
import argparse
import random
from pathlib import Path

from Projects.base.game.darkHex import C_PLAYER1, C_PLAYER2, DarkHex
from Projects.base.util.drive import download_file_from_google_drive

TEST_MODE = True

customP1 = []; customP2 = [];
# customP1 = ['.','.','.',
#               '.','.','.',
#                 '.','.','.',
#                   '.','.','.',]
# customP2 = ['.','.','.',
#               '.','.','.',
#                 '.','.','.',
#                   '.','.','.',]

def one_move(chc_state, current_state):
    # find the new move
    assert(len(chc_state) == len(current_state))
    changed = False
    for i in range(len(chc_state)):
        if chc_state[i] != current_state[i]:
            if changed or current_state[i] != '.':
                return False
            changed = True
            move = i
    return move

def player_play(e, h, results, game_board):
    for res in results[e-1][h]:
        if results[e-1][h][res] == C_PLAYER1:
            mv = one_move(res, game_board)
            if mv:
                print('Sure win move exists for current game')
                return mv 
    return random.randint(0, len(game_board)-1)

def play_vs_pONE(results, num_rows, num_cols):
    game = DarkHex(BOARD_SIZE=[num_rows,num_cols],
                   custom_board_C_PLAYER1=customP1,
                   custom_board_C_PLAYER2=customP2)
    
    e = game.BOARD.count('.')
    result = '='

    i = 0
    print('Player 1 (B) is played by the pONE agent\n\
Player 2 (B) is you, please make a move according\n\
to the given table indexes. For 3x4 board here\n\
are the board indexes;\n\n\
B   B   B  \n\
------------\n\
W\ 0   1   2  \W\n\
 W\ 3   4   5  \W\n\
  W\ 6   7   8  \W\n\
   W\ 9  10   11 \W\n\
     --------------\n\
        B   B   B' )
    while result == '=':
        if i % 2 == 0:
            result = 'f'
            while result == 'f':
                action = player_play(e, game.totalHidden_for_player(C_PLAYER1), 
                                     results, game.BOARDS[C_PLAYER1])
                board, done, result, reward = game.step(C_PLAYER1, action)
        else:
            result = 'f'
            while result == 'f':
                try:
                    action = int(input('move: ').strip())
                    board, done, result, reward = game.step(C_PLAYER2, action)
                except KeyboardInterrupt:
                    exit()
                except:
                    print("Please enter a valid input, the format should be an int. i.e. 3")
                    continue
            game.print_information_set(C_PLAYER1)
        if TEST_MODE:
            game.printBoard()
        e -= 1; i += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_file", "-if", type=str,
                        help="File path to load the results from")
    args = parser.parse_args()
    
    if not args.in_file:
        print('Please pick a pre-run game data to work on;')        
        print('\t1) 3x3 First Player')
        print('\t2) 4x3 First Player (Long edge)')
        game_type = -1
        while game_type <= 0 or game_type > 2:
            try:
                game_type = int(input('Please enter the item number only (i.e. 1): ').strip())
            except KeyboardInterrupt:
                exit()
            except:
                game_type = -1
                print('Invalid input, please try again.')
        if game_type == 1:
            Path('Exp_Results/pONE/3x3/').mkdir(parents=True, exist_ok=True)
            args.in_file = 'Exp_Results/pONE/3x3/default_file.pkl'
            download_file_from_google_drive('1oNl4UZAB6SxjA-aUi0M9oUiqlpIdXnwk', args.in_file)
        elif game_type == 2:
            Path('Exp_Results/pONE/4x3/').mkdir(parents=True, exist_ok=True)
            args.in_file = 'Exp_Results/pONE/4x3/default_file.pkl'
            download_file_from_google_drive('1MpMn8Gf0a8tCWeb8Ag276FlLGX6tBCD9', args.in_file)
            
    with open(args.in_file, 'rb') as f:
        dct = pickle.load(f)

    results = dct['results']
    num_cols = dct['num_cols']
    num_rows = dct['num_rows']

    play_vs_pONE(results, num_rows, num_cols)