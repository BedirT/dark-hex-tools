from time import sleep
from Projects.pONE.pONE import tup_to_str
from copy import copy
import curses

from Projects.pONE.user_tools.glance import glance
from Projects.base.game.hex import customBoard_print, print_init_board
from Projects.base.util.colors import colors, pieces
from Projects.base.util.curses_func import *

from Projects.pONE.ui.menus import data_menu, customBoard_menu

TEST_MODE = True

C_PLAYER1 = pieces.C_PLAYER1
C_PLAYER2 = pieces.C_PLAYER2

def player_play(e, h, results, game_board):
    res = copy(game_board)
    for mv in range(len(game_board)):
        if game_board[mv] == '.':
            res[mv] = C_PLAYER1
            if tuple(res) in results[e-1][h] and \
                results[e-1][h][tuple(res)][0] == C_PLAYER1:
                return mv 
            res[mv] = '.'

def play_vs_pONE(stdscr, results, num_rows, num_cols):
    game = curses.wrapper(customBoard_menu, num_rows, num_cols)
    
    e = game.BOARD.count('.')
    result = '='

    i = 0
    
    print_init_board_middle(stdscr, game.num_cols, game.num_rows)
    sleep(2)
    move_order = []
    while result == '=':
        if i % 2 == 0:
            result = 'f'
            while result == 'f':
                action = player_play(e, game.totalHidden_for_player(C_PLAYER1), 
                                     results, game.BOARDS[C_PLAYER1])
                print_center(stdscr, action)
                sleep(5)
                _, _, result, _ = game.step(C_PLAYER1, action)
                move_order.append(action)
        else:
            result = 'f'
            while result == 'f':
                action = print_board_middle(stdscr, game.BOARD, game.num_cols, game.num_rows)
                if action == -1:
                    if len(move_order) == 0:
                        warning = 'No stones placed yet.'
                    if len(move_order) == 1:
                        r = move_order.pop()
                        warning = 'Rewinding the move: {}'.format(r)
                        game.rewind(r)
                    else:
                        r = move_order.pop()
                        warning = 'Rewinding the move: {}'.format(r)
                        game.rewind(r)
                        r = move_order.pop()
                        warning += ' & Rewinding the move: {}'.format(r)
                        game.rewind(r)
                    continue
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