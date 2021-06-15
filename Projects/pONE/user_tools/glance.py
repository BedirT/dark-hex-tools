# Just to see what we have as definite win moves
from Projects.base.util.colors import colors, pieces
from Projects.base.game.hex import customBoard_print
from Projects.pONE.ui.menus import data_menu

from Projects.base.util.curses_func import *
import curses

def glance(stdscr):
    dct = data_menu(stdscr)

    results = dct['results']
    num_cols = dct['num_cols'] 
    num_rows = dct['num_rows']
    visible_player = dct['visible_player']
    hidden_player = dct['hidden_player']
    num_of_moves = num_cols * num_rows

    input_item = text_box(stdscr, "Please enter number of empty cells (e)", 10,
                            extra_notes= "Please type 'all' to include all possible e and h values.")
    e = input_item.strip()
    if e.lower() == 'all':
        e = -1
        h = -1
    else:
        e = int(e)
        input_item = text_box(stdscr, "Please enter number of hidden cells (h)", 10)                        
        h = int(input_item.strip())

    if e == -1 and h == -1:
        for e in range(num_of_moves):
            for h in range(num_of_moves//2):
                for res in results[e][h]:
                    if results[e][h][res][0] in [visible_player, hidden_player]:
                        customBoard_print_curses(stdscr, res, num_cols, num_rows)
    else:
        for res in results[e][h]:
            if results[e][h][res][0] == visible_player:
                customBoard_print_curses(stdscr, res, num_cols, num_rows)
        

    
