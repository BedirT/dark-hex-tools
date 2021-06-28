import curses
import Projects.pONE.ui.main_menu as mm

from Projects.base.util.curses_func import *

def main_menu(stdscr):
    main_menu = ['{:^{}}'.format('pONE', 25), '{:^{}}'.format('@BedirT', 25), 
        'Train with pONE', 'Play against pONE', 'Have a glance at the data',
        'Plot heatmaps', 'Exit']

    # turn off cursor blinking
    curses.curs_set(0)

    # color scheme for selected row
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE) 
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)

    curses.init_pair(pairs.C_PLAYER1, curses.COLOR_WHITE, curses.COLOR_BLUE) # c1
    curses.init_pair(pairs.C_PLAYER2, curses.COLOR_BLACK, curses.COLOR_CYAN) # c2
    curses.init_pair(pairs.NEUTRAL, curses.COLOR_BLACK, curses.COLOR_WHITE) # neut

    curses.init_pair(pairs.C_PLAYER1_selected, curses.COLOR_BLUE, curses.COLOR_WHITE) # c1
    curses.init_pair(pairs.C_PLAYER2_selected, curses.COLOR_CYAN, curses.COLOR_BLACK)   # c2
    curses.init_pair(pairs.NEUTRAL_selected, curses.COLOR_WHITE, curses.COLOR_BLACK) # neut

    # specify the current selected row
    current_row = 2

    # print the menu
    print_menu(stdscr, current_row, main_menu,
                   [0, 1], [2, 2])

    while 1:
        key = stdscr.getch()
        
        if key == curses.KEY_UP and current_row > 2:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(main_menu)-1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_row == 2: # train
                mm.train(stdscr)
            elif current_row == 3: # play
                mm.play(stdscr)
            elif current_row == 4: # glance
                mm.glance(stdscr)
            # elif current_row == 5: # heatmap
            #     mm.plot(stdscr)

            stdscr.getch()
            # if user selected last row, exit the program
            if current_row == len(main_menu)-1:
                break

        print_menu(stdscr, current_row, main_menu,
                   [0, 1], [2, 2])

curses.wrapper(main_menu)