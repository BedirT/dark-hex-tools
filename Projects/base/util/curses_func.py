import curses
from curses.textpad import Textbox, rectangle
from Projects.base.util.colors import pieces

class pairs:
    C_PLAYER1 = 3
    C_PLAYER2 = 4
    NEUTRAL = 5
    C_PLAYER1_selected = 6
    C_PLAYER2_selected = 7
    NEUTRAL_selected = 8

def print_menu(stdscr, selected_row_idx, menu, 
               ignore_items=None, colors_for_ignored=None):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    for idx, row in enumerate(menu):
        x = w//2 - len(row)//2
        y = h//2 - len(menu)//2 + idx
        set_item = False
        if ignore_items:
            for ignore, c in zip(ignore_items, colors_for_ignored):
                if idx == ignore:
                    stdscr.attron(curses.color_pair(c))
                    stdscr.addstr(y, x, row)
                    stdscr.attroff(curses.color_pair(c))
                    set_item = True
                    continue
        if set_item:
            continue
        elif idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, row)
    stdscr.refresh()

def print_center(stdscr, text):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    x = w//2 - len(text)//2
    y = h//2
    stdscr.addstr(y, x, text)
    stdscr.refresh()

def print_center_xy(stdscr, texts):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    for i, text in enumerate(texts):
        x = w//2 - len(text)//2
        y = h//2 - len(texts)//2 + i
        stdscr.addstr(y, x, text)
    stdscr.refresh()

def print_center_xy_sideBySide(stdscr, texts1, texts2):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    mx_len = max(len(texts1),len(texts2))
    for i, (text1, text2) in zip(enumerate(texts1, texts2)):
        x1 = w//2 - len(text1)//2 + len(text2)
        x2 = x1 + 10
        y = h//2 - len(mx_len)//2 + i
        stdscr.addstr(y, x1, text1)
        stdscr.addstr(y, x2, text2)
    stdscr.refresh()

def print_init_board_middle(stdscr, num_cols, num_rows):
    num_cells = num_cols * num_rows

    stdscr.clear()
    h, w = stdscr.getmaxyx()

    x = w//2 - ((num_cells-1)//num_cols + (num_cols+1) * 3)//2
    y = h//2 - num_cols//2 - 3

    extra_text = [  'Player 1 (B) is played by the pONE agent',
                    'Player 2 (W) is you, please make a move',
                    'according to the given table indexes. Here',
                    'are the board indexes;']

    y -= len(extra_text)//2
    for e in extra_text:
        ex = w//2 - len(e)//2
        stdscr.addstr(y, ex, e)
        y+=1

    stdscr.addstr(y, x, '  ' + '{0: <3}'.format(pieces.C_PLAYER1) * num_cols)
    stdscr.addstr(y+1, x, ' ' + '-' * (num_cols * 3 +1))
    
    cell = 0
    for row in range(num_rows):
        for col in range(num_cols):
            if col == 0: # first col
                spaces = cell//num_cols
                stdscr.addstr(y+2+row, x+spaces, pieces.C_PLAYER2 + '\ ')
            stdscr.addstr(y+2+row, x+(col+1)*3+spaces, '{0: <3}'.format(cell))
            if col == num_cols-1: # last col
                stdscr.addstr(y+2+row, x+(col+1)*3+2+spaces, '\\' + pieces.C_PLAYER2)
            cell += 1
    y+=row
    
    stdscr.addstr(y+3, x+spaces+2, '-' * (num_cols * 3 +1))
    stdscr.addstr(y+4, x, ' ' * (num_rows+4) + '{0: <3}'.format(pieces.C_PLAYER1) * num_cols)

    stdscr.refresh()

def print_board(stdscr, cur_row, cur_col, board, warning=None):
    num_rows = len(board)
    num_cols = len(board[0])
    num_cells = num_cols * num_rows

    stdscr.clear()
    h, w = stdscr.getmaxyx()

    x = w//2 - ((num_cells-1)//num_cols + (num_cols+1) * 3)//2
    y = h//2 - num_cols//2 - 3

    stdscr.addstr(y, x, '  ' + '{0: <3}'.format(pieces.C_PLAYER1) * num_cols)
    stdscr.addstr(y+1, x, ' ' + '-' * (num_cols * 3 +1))
    
    cell = 0
    for row in range(num_rows):
        for col in range(num_cols):
            if col == 0: # first col
                spaces = cell//num_cols
                stdscr.addstr(y+2+row, x+spaces, pieces.C_PLAYER2 + '\ ')
            elif col == num_cols-1: # last col
                stdscr.addstr(y+2+row, x+(col+1)*3+2+spaces, '\\' + pieces.C_PLAYER2)
            else:
                if row-1 == cur_row and col-1 == cur_col:
                    if board[cell] == pieces.C_PLAYER1:
                        clr = pairs.C_PLAYER1_selected # player1
                    elif board[cell] == pieces.C_PLAYER2:
                        clr = pairs.C_PLAYER2_selected # player2
                    else:
                        clr = pairs.NEUTRAL_selected # neutral
                if board[cell] == pieces.C_PLAYER1:
                    clr = pairs.C_PLAYER1 # player1
                elif board[cell] == pieces.C_PLAYER2:
                    clr = pairs.C_PLAYER2 # player2
                else:
                    clr = pairs.NEUTRAL # neutral
                stdscr.attron(curses.color_pair(clr))  
                stdscr.addstr(y+2+row, x+(col+1)*3+spaces, '{0: <3}'.format(cell))
                stdscr.attron(curses.color_pair(clr))
            cell += 1
    y+=row

    stdscr.addstr(y+3, x+spaces+2, '-' * (num_cols * 3 +1))
    stdscr.addstr(y+4, x, ' ' * (num_rows+4) + '{0: <3}'.format(pieces.C_PLAYER1) * num_cols)

    # if warning:
    #     stdscr.attron(curses.color_pair(2))  
    #     stdscr.addstr(y + 3, x, warning)
    #     stdscr.attron(curses.color_pair(2))  
    stdscr.refresh()

def text_box(stdscr, input_text, box_size, extra_notes=None):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    x = w//2 - len(input_text)//2
    y = h//2

    stdscr.addstr(y - 4, x, input_text)

    editwin = curses.newwin(1, box_size, y-1, w//2-(box_size//2))
    rectangle(stdscr, y-2 , w//2-(box_size//2)-3, y, w//2+(box_size//2)+3)
  
    stdscr.addstr(y + 2, x, 'Control-H: Delete character backward.')
    stdscr.addstr(y + 3, x, 'Control-L: Refresh screen.')
    stdscr.addstr(y + 4, x, 'Control-A: Go to left edge of window.')
    stdscr.addstr(y + 5, x, 'Control-F: KEY_RIGHT.')
    stdscr.addstr(y + 6, x, 'Control-B: KEY_LEFT')

    if extra_notes:
        for i, e in enumerate(extra_notes):
            x = w//2 - len(e)//2
            stdscr.attron(curses.color_pair(2))
            stdscr.addstr(y + 8 + i, x, e)  
            stdscr.attroff(curses.color_pair(2))
            

    stdscr.refresh()

    box = Textbox(editwin)

    # Let the user edit until Ctrl-G is struck.
    box.edit()

    # Get resulting contents
    return box.gather()

def customBoard_print_curses(stdscr, board, num_cols, num_rows):
    '''
    Method for printing the board in a nice format.
    '''
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    x = w//2 - num_cols//2
    y = h//2 - num_rows//2
    num_cells = num_cols * num_rows
    stdscr.addstr(y, x, '  ' + '{0: <3}'.format(pieces.C_PLAYER1) * num_cols)

    # print(colors.BOLD + colors.C_PLAYER1 + ' ' + '-' * (num_cols * 3 +1) + colors.ENDC)
    # for cell in range(num_cells):
    #     if cell % num_cols == 0: # first col
    #         print(colors.BOLD + colors.C_PLAYER2 + pieces.C_PLAYER2 + '\ ' + colors.ENDC, end= '')
    #     if board[cell] == pieces.C_PLAYER1:
    #         clr = colors.C_PLAYER1
    #     elif board[cell] == pieces.C_PLAYER2:
    #         clr = colors.C_PLAYER2
    #     else:
    #         clr = colors.NEUTRAL
    #     print(clr + '{0: <3}'.format(board[cell]) + colors.ENDC, end='') 
    #     if cell % num_cols == num_cols-1: # last col
    #         print(colors.BOLD + colors.C_PLAYER2 + '\\' + pieces.C_PLAYER2 + '\n' + (' ' * (cell//num_cols)) + colors.ENDC, end = ' ')
    # print(colors.BOLD + colors.C_PLAYER1 + '  ' + '-' * (num_cols * 3 +1) + colors.ENDC)        
    # print(colors.BOLD + colors.C_PLAYER1 + ' ' * (num_rows+4) + '{0: <3}'.format(pieces.C_PLAYER1) * num_cols + colors.ENDC)
    stdscr.refresh()