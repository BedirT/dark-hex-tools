import pickle
import random
from copy import copy

from Projects.pONE.user_tools.glance import glance
from Projects.base.game.hex import customBoard_print, print_init_board
from Projects.base.game.darkHex import DarkHex
from Projects.base.util.drive import missing_in_file
from Projects.base.util.print_tools import wrap_it, question_cont
from Projects.base.util.colors import colors, pieces

preset_boards = [
    [('.','W','.','W','.','.','.','.','B','B','.','.'), 
     ('.','W','.','W','.','.','.','.','B','B','.','.')],
    [('W','.','.','W','.','.','.','.','B','B','.','.'), 
     ('W','.','.','W','.','.','.','.','B','B','.','.')],
    [('.','.','.','.','.','W','W','B','.','.','.','B'), 
     ('.','.','.','.','.','W','W','B','.','.','.','B')],
    [('.','.','.','.','.','.','W','B','W','.','B','.'), 
     ('.','.','.','.','.','.','W','B','W','.','B','.')],
    [('.','W','.','.','.','.','W','B','.','.','B','.'), 
     ('.','W','.','.','.','.','W','B','.','.','B','.')],
    [('.','.','.','.','W','.','B','.','.','B','W','.'), 
     ('.','.','.','.','W','.','B','.','.','B','W','.')],
]

TEST_MODE = True

C_PLAYER1 = pieces.C_PLAYER1
C_PLAYER2 = pieces.C_PLAYER2

def player_play(e, h, results, game_board):
    res = copy(game_board)
    for mv in range(len(game_board)):
        if game_board[mv] == '.':
            res[mv] = C_PLAYER1
            if tuple(res) in results[e-1][h] and results[e-1][h][tuple(res)] == C_PLAYER1:
                print('Sure win move exists for current game')
                return mv 
            res[mv] = '.'

def set_custom_boards(game):
    while True:
        wrap_it('\t1) Enter your own boards', colors.QUESTIONS)
        wrap_it('\t2) Choose from prewritten (Win moves)', colors.QUESTIONS)
        wrap_it('\t3) Choose by glancing', colors.QUESTIONS)
        ans = input().strip()
        if ans == '1':
            while True:
                warning_text = 'The input should be in a string format without any spaces, dot ({}) specifies an empty cell, {} for player 1 and {} for player 2 stones. Do not use any other character. Entered board size (number of cells) should match the size of the string entered.'.format("'.'", C_PLAYER1, C_PLAYER2)
                wrap_it(warning_text, colors.QUESTIONS)
                # BOARD 1
                wrap_it('Enter board for player 1: ', colors.QUESTIONS)
                board1 = input().strip()
                if len(board1) != game.num_rows * game.num_cols:
                    wrap_it('Please enter a valid board, the string size doesnt match.', colors.WARNING)
                    continue
                ct = board1.count('.') + board1.count(C_PLAYER1) + board1.count(C_PLAYER2)
                if ct != game.num_rows * game.num_cols:
                    wrap_it('Please enter a valid board, there is an invalid char.', colors.WARNING)
                    continue
                # BOARD 2
                wrap_it('Enter board for player 1: ', colors.QUESTIONS)
                board2 = input().strip()
                if len(board2) != game.num_rows * game.num_cols:
                    wrap_it('Please enter a valid board, the string size doesnt match.', colors.WARNING)
                    continue
                ct = board2.count('.') + board2.count(C_PLAYER1) + board2.count(C_PLAYER2)
                if ct != game.num_rows * game.num_cols:
                    wrap_it('Please enter a valid board, there is an invalid char.', colors.WARNING)
                    continue
                # check if the boards are matching
                suc = game.set_board([*board1], [*board2])
                if not suc:
                    wrap_it('Entered boards doesnt match. Please re-enter.', colors.WARNING)
                    continue
                wrap_it('Custom boards successfully set!', colors.SUCCESS)
                break
            break
        elif ans == '2':
            wrap_it('Please pick from the list of provided board positions.:', colors.MIDTEXT)
            while True:
                for i, board_pos in enumerate(preset_boards):
                    print(colors.MIDTEXT + colors.BOLD + '{})'.format(i) + colors.ENDC)
                    print(colors.C_PLAYER1 + colors.BOLD + 'Board for player 1' + colors.ENDC)
                    customBoard_print(board_pos[0], game.num_cols, game.num_rows)
                    print(colors.C_PLAYER2 + colors.BOLD + 'Board for player 2' + colors.ENDC)
                    customBoard_print(board_pos[1], game.num_cols, game.num_rows)
                choice = question_cont('Enter your choice:', int)
                if choice < 0 or choice >= len(preset_boards):
                    wrap_it('Invalid input please try again.', colors.WARNING)
                    continue
                board1 = preset_boards[choice][0]
                board2 = preset_boards[choice][1]
                suc = game.set_board([*board1], [*board2])
                break
            break
        elif ans == '3':
            ch = 0
            if game.num_rows == 4 and game.num_cols == 3:
                ch = 2
            elif game.num_rows == 3 and game.num_cols == 3:
                ch = 1
            new_res, h = glance(board_type=ch)
            while True:
                try:
                    choice = question_cont('Enter your choice:', int)
                    board2 = new_res[choice]
                    board1 = calc_new_board(board2, C_PLAYER1, h)
                    suc = game.set_board([*board1], [*board2])
                    break
                except KeyboardInterrupt:
                    exit()
                except:
                    wrap_it('Invalid value. Try again.', colors.WARNING)
            break
        else:
            wrap_it('Please enter a valid value.', colors.WARNING)
    return game

def calc_new_board(board, clr, h):
    tmp = copy.copy(board)
    for _ in range(h):
        while True:
            idx = random.randint(0, len(board)-1)
            if tmp[idx] == '.':
                tmp[idx] = clr
                break
    return tmp

def play_vs_pONE(results, num_rows, num_cols):
    game = DarkHex(BOARD_SIZE=[num_rows,num_cols])
    
    while True:
        wrap_it('Do you want to start from a custom board?', colors.QUESTIONS) 
        wrap_it('\t1) Yes', colors.QUESTIONS)
        wrap_it('\t2) No', colors.QUESTIONS)
        ans = input().strip()
        if ans == '1':
            game = set_custom_boards(game)
            break
        elif ans == '2':
            break
        else:
            wrap_it('Please enter a valid value.', colors.WARNING)
    
    e = game.BOARD.count('.')
    result = '='

    i = 0
    print('Player 1 (B) is played by the pONE agent\n\
    Player 2 (B) is you, please make a move according\n\
    to the given table indexes. For 3x4 board here\n\
    are the board indexes;\n')
    print_init_board(game.num_cols, game.num_rows)

    while result == '=':
        if i % 2 == 0:
            result = 'f'
            while result == 'f':
                action = player_play(e, game.totalHidden_for_player(C_PLAYER1), 
                                     results, game.BOARDS[C_PLAYER1])
                _, _, result, _ = game.step(C_PLAYER1, action)
        else:
            result = 'f'
            while result == 'f':
                try:
                    action = int(input('move: ').strip())
                    _, _, result, _ = game.step(C_PLAYER2, action)
                except KeyboardInterrupt:
                    exit()
                except:
                    print("Please enter a valid input, the format should be an int. i.e. 3. Valid indexes shown as in the board below;")
                    print_init_board(game.num_cols, game.num_rows, game.C_PLAYER1, game.C_PLAYER2)
                    continue
            game.print_information_set(C_PLAYER1)
        if TEST_MODE:
            game.printBoard()
        e -= 1; i += 1

def play_pONE(in_file=None):
    if not in_file:
        in_file = missing_in_file()
            
    with open(in_file, 'rb') as f:
        dct = pickle.load(f)

    results = dct['results']
    num_cols = dct['num_cols']
    num_rows = dct['num_rows']

    play_vs_pONE(results, num_rows, num_cols)