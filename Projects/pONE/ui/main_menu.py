'''
Single py file to combine all pONE projects.

The file will direct user on a menu to find the options the user is
interested in.
'''
from Projects.pONE.user_tools.glance import glance
from Projects.base.util.cPlot import heat_map
from Projects.pONE.user_tools.trainer import train_pONE
from Projects.pONE.user_tools.play import C_PLAYER1, C_PLAYER2, play_pONE

from Projects.base.util.curses_func import *

import curses

def train(stdscr):
    curses.curs_set(1)
    input_item = text_box(stdscr, "Please enter number of columns", 10)
    cols = int(input_item.strip())
    input_item = text_box(stdscr, "Please enter number of rows", 10)
    rows = int(input_item.strip())
    input_item = text_box(stdscr, "Which player is the visible player?", 10, 
                          extra_notes= ["Please choose between {} and {}".format(C_PLAYER1, C_PLAYER2)])
    vis_player = input_item.strip()
    input_item = text_box(stdscr, "Please enter the output destination (optional - leave it empty)", 40)
    output_file = input_item.strip()
    curses.curs_set(0)
    train_pONE(output_file, rows, cols, vis_player)
    
def play(stdscr):
    play_pONE(stdscr)

def glance_menu(stdscr):
    glance(stdscr)

def plot(stdscr):
    heat_map(stdscr)