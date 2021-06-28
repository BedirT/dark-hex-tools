from copy import copy
import curses
from time import sleep

from Projects.pONE.user_tools.glance import glance
from Projects.base.game.hex import customBoard_print, print_init_board
from Projects.base.util.colors import colors, pieces
from Projects.base.util.curses_func import *

from Projects.pONE.ui.menus import data_menu, customBoard_menu

TEST_MODE = True

C_PLAYER1 = pieces.C_PLAYER1
C_PLAYER2 = pieces.C_PLAYER2

def player_play(stdscr, e, h, results, game_board):
    for mv in range(len(game_board)):
        if game_board[mv] == '.':
            game_board[mv] = C_PLAYER1
            if tuple(game_board) in results[e-1][h]:
                print_center(stdscr, results[e-1][h][tuple(game_board)][0])
                sleep(2)
                print_center(stdscr, '.')
                sleep(1)
                if results[e-1][h][tuple(game_board)][0] == C_PLAYER1:
                    return mv 
            game_board[mv] = '.'
    exit()

def move_on_board(stdscr, board, text_on_top=None):
    curses.curs_set(0)
    current_row = 0
    start_row_from = 0

    if text_on_top:
        board.insert(0, text_on_top)
        current_row = 1
        start_row_from = 1

    current_col = 0
    board.append('Exit')

    num_rows = len(board)
    num_cols = len(board[0])

    warning = None
    
    print_board(stdscr, current_row, current_col, board, warning=warning)

    while 1:
        key = stdscr.getch()
        
        if key == curses.KEY_UP and current_row > start_row_from:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(num_rows)-1:
            current_row += 1
        elif key == curses.KEY_LEFT and current_col > 0:
            current_col -= 1
        elif key == curses.KEY_RIGHT and current_col < len(num_cols[0])-1:
            current_col += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            # play to cur_col, cur_row
            # return to the action
            action = num_cols * current_row + current_col
            if board[action] == '.':
                return action
            else:
                # warn
                # continue
                warning = 'You cannot move to an occupied cell.'
            stdscr.getch()
            # if user selected last row, back the program
            if current_row == len(board)-1:
                break

        print_board(stdscr, current_row, current_col, board, warning)


def play_vs_pONE(stdscr, results, num_rows, num_cols):
    game = curses.wrapper(customBoard_menu, num_rows, num_cols)
    
    e = game.BOARD.count('.')
    result = '='

    i = 0
    
    print_init_board_middle(stdscr, game.num_cols, game.num_rows)
    move_order = []
    while result == '=':
        if i % 2 == 0:
            result = 'f'
            while result == 'f':
                action = player_play(stdscr, e, game.totalHidden_for_player(C_PLAYER1), 
                                     results, game.BOARDS[C_PLAYER1])
                _, _, result, _ = game.step(C_PLAYER1, action)
                move_order.append(action)
        else:
            result = 'f'
            while result == 'f':
                action = move_on_board(stdscr, game.BOARDS[C_PLAYER2], '{}\'s move'.format(C_PLAYER1))
                # if action == -1: # rewinding
                #     if len(move_order) == 0:
                #         warning = 'No stones placed yet.'
                #     if len(move_order) == 1:
                #         r = move_order.pop()
                #         warning = 'Rewinding the move: {}'.format(r)
                #         game.rewind(r)
                #     else:
                #         r = move_order.pop()
                #         warning = 'Rewinding the move: {}'.format(r)
                #         game.rewind(r)
                #         r = move_order.pop()
                #         warning += ' & Rewinding the move: {}'.format(r)
                #         game.rewind(r)
                #     continue
                _, _, result, _ = game.step(C_PLAYER2, action)
                move_order.append(action)
            # game.print_information_set(C_PLAYER1)
        
        # if TEST_MODE:
        #     game.printBoard()
        e -= 1; i += 1

    print_center(stdscr, 'Winner is ' + result.upper())

def play_pONE(stdscr):
    dct = curses.wrapper(data_menu)

    results = dct['results']
    num_cols = dct['num_cols']
    num_rows = dct['num_rows']

    play_vs_pONE(stdscr, results, num_rows, num_cols)