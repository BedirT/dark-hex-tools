from Projects.base.util.colors import colors
from pathlib import Path
from Projects.base.util.curses_func import *
from Projects.base.util.drive import download_file_from_google_drive
from Projects.base.game.darkHex import DarkHex
import pickle
import curses

def data_menu(stdscr):
    menu = [
        '3x3 first player', 
        '3x3 second player',
        '3x4 first player',
        '3x4 second player',
        '4x3 first player',
        '4x3 second player',
        'Cancel']

    curses.curs_set(0)
    current_row = 0
    print_menu(stdscr, current_row, menu)

    while 1:
        key = stdscr.getch()
        
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu)-1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_row == 0: # 3x3 fp
                Path('Exp_Results/pONE/3x3/').mkdir(parents=True, exist_ok=True)
                in_file = 'Exp_Results/pONE/3x3/firstPlayer.pkl'
                my_file = Path(in_file)
                if not my_file.is_file():
                    download_file_from_google_drive('1lYwM-hztNPJU4n04is0__iw2B7ofiJQf', in_file)
                with open(in_file, 'rb') as f:
                    dct = pickle.load(f)
                return dct
            elif current_row == 1: # 3x3 sp
                Path('Exp_Results/pONE/3x3/').mkdir(parents=True, exist_ok=True)
                in_file = 'Exp_Results/pONE/3x3/secondPlayer.pkl'
                my_file = Path(in_file)
                if not my_file.is_file():
                    download_file_from_google_drive('1gkcSdUXI2W960eOmjNHBkxLo1D7M-eYn', in_file)
                with open(in_file, 'rb') as f:
                    dct = pickle.load(f)
                return dct
            # elif current_row == 2: # 3x4 fp
            #     Path('Exp_Results/pONE/3x4/').mkdir(parents=True, exist_ok=True)
            #     in_file = 'Exp_Results/pONE/3x4/firstPlayer.pkl'
            #     my_file = Path(in_file)
            #     if not my_file.is_file():
            #         download_file_from_google_drive('14GjgZtnWVKOaJzvZ67MJPqU6zUdPsIU4', in_file)
            #     with open(in_file, 'rb') as f:
            #         dct = pickle.load(f)
            #     return dct
            # elif current_row == 3: # 3x4 sp
            #     Path('Exp_Results/pONE/3x4/').mkdir(parents=True, exist_ok=True)
            #     in_file = 'Exp_Results/pONE/3x4/secondPlayer.pkl'
            #     my_file = Path(in_file)
            #     if not my_file.is_file():
            #         download_file_from_google_drive('14GjgZtnWVKOaJzvZ67MJPqU6zUdPsIU4', in_file)
            #     with open(in_file, 'rb') as f:
            #         dct = pickle.load(f)
            #     return dct
            # elif current_row == 4: # 4x3 fp
            #     Path('Exp_Results/pONE/4x3/').mkdir(parents=True, exist_ok=True)
            #     in_file = 'Exp_Results/pONE/4x3/firstPlayer.pkl'
            #     my_file = Path(in_file)
            #     if not my_file.is_file():
            #         download_file_from_google_drive('14GjgZtnWVKOaJzvZ67MJPqU6zUdPsIU4', in_file)
            #     with open(in_file, 'rb') as f:
            #         dct = pickle.load(f)
            #     return dct
            # elif current_row == 5: # 4x3 sp
            #     Path('Exp_Results/pONE/4x3/').mkdir(parents=True, exist_ok=True)
            #     in_file = 'Exp_Results/pONE/4x3/secondPlayer.pkl'
            #     my_file = Path(in_file)
            #     if not my_file.is_file():
            #         download_file_from_google_drive('14GjgZtnWVKOaJzvZ67MJPqU6zUdPsIU4', in_file)
            #     with open(in_file, 'rb') as f:
            #         dct = pickle.load(f)
            #     return dct
            stdscr.getch()
            # if user selected last row, back the program
            if current_row == len(menu)-1:
                break

        print_menu(stdscr, current_row, menu)

# def set_custom_boards_menu(stdscr):
    
    #     elif ans == '3':
    #         new_res, h = glance()
    #         while True:
    #             try:
    #                 choice = question_cont('Enter your choice:', int)
    #                 board2 = new_res[choice]
    #                 board1 = calc_new_board(board2, C_PLAYER1, h)
    #                 suc = game.set_board([*board1], [*board2])
    #                 break
    #             except KeyboardInterrupt:
    #                 exit()
    #             except:
    #                 wrap_it('Invalid value. Try again.', colors.WARNING)
    #         break
    #     else:
    #         wrap_it('Please enter a valid value.', colors.WARNING)
    # return game

# def calc_new_board(board, clr, h):
#     tmp = copy.copy(board)
#     for _ in range(h):
#         while True:
#             idx = random.randint(0, len(board)-1)
#             if tmp[idx] == '.':
#                 tmp[idx] = clr
#                 break
#     return tmp

def set_custom_boards_menu(stdscr, num_rows, num_cols):
    game = DarkHex(BOARD_SIZE=[num_rows,num_cols])
    menu = [
        'Enter your own boards',
        'Choose from prewritten (Win moves)', 
        'Choose by glancing',
        'Cancel']

    curses.curs_set(0)
    current_row = 0
    print_menu(stdscr, current_row, menu)

    while 1:
        key = stdscr.getch()
        
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu)-1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_row == 0: # enter board
                board1 = None; board2 = None
                while True:
                    warning_texts = ['The input should be in a string format without any spaces.',
                                     '\'{}\' specifies an empty cell, {} for player 1 and {} for player 2 stones'.format(pieces.NEUTRAL, pieces.C_PLAYER1, pieces.C_PLAYER2),
                                     'Do not use any other character.',
                                     'Entered board size (number of cells) should match the size of the string entered.']
                    # BOARD 1
                    if not board1:
                        board1 = text_box(stdscr, 'Please enter the board for player 1 ({}) in string format'.format(pieces.C_PLAYER1), 40, extra_notes=warning_texts)
                        if len(board1) != game.num_rows * game.num_cols:
                            warning_texts += colors.WARNING + 'Please enter a valid board, the string size doesnt match.' + colors.ENDC
                            board1 = None
                            continue
                        ct = board1.count('.') + board1.count(pieces.C_PLAYER1) + board1.count(pieces.C_PLAYER2)
                        if ct != game.num_rows * game.num_cols:
                            warning_texts += colors.WARNING + 'Please enter a valid board, there is an invalid char.' + colors.ENDC
                            board1 = None
                            continue
                    # BOARD 2
                    if not board2:
                        board2 = text_box(stdscr, 'Please enter the board for player 2 ({}) in string format'.format(pieces.C_PLAYER2), 40, extra_notes=warning_text)
                        if len(board2) != game.num_rows * game.num_cols:
                            warning_texts += colors.WARNING + 'Please enter a valid board, the string size doesnt match.' + colors.ENDC
                            board2 = None
                            continue
                        ct = board2.count('.') + board2.count(pieces.C_PLAYER1) + board1.count(pieces.C_PLAYER2)
                        if ct != game.num_rows * game.num_cols:
                            warning_texts += colors.WARNING + 'Please enter a valid board, there is an invalid char.' + colors.ENDC
                            board2 = None
                            continue
                    # check if the boards are matching
                    suc = game.set_board([*board1], [*board2])
                    if not suc:
                        warning_texts += colors.WARNING + 'Entered boards doesnt match. Please re-enter.' + colors.ENDC
                        board1 = None; board2 = None
                        continue
                    return game
            elif current_row == 2: # prewritten
                return pick_from_preset_menu(stdscr, game)
            stdscr.getch()
            # if user selected last row, back the program
            if current_row == len(menu)-1:
                break

        print_menu(stdscr, current_row, menu)

def pick_from_preset_menu(stdscr, game):
    menu = [
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
        'Exit'
    ]

    curses.curs_set(0)
    current_row = 0
    print_menu(stdscr, current_row, menu)

    while True:
        key = stdscr.getch()
        
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu)-1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_row != len(menu)-1:
                board1 = menu[current_row][0]
                board2 = menu[current_row][1]
                _ = game.set_board([*board1], [*board2])
                return game
            stdscr.getch()
            # if user selected last row, back the program
            if current_row == len(menu)-1:
                break

        print_menu(stdscr, current_row, menu)

def customBoard_menu(stdscr, num_rows, num_cols):
    game = DarkHex(BOARD_SIZE=[num_rows,num_cols])
    menu = [
        'Do you want to start from a custom board?',
        'Yes', 
        'No',
        'Cancel']

    curses.curs_set(0)
    current_row = 1
    print_menu(stdscr, current_row, menu)

    while 1:
        key = stdscr.getch()
        
        if key == curses.KEY_UP and current_row > 1:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu)-1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_row == 1:
                game = set_custom_boards_menu(stdscr, num_rows, num_cols)
            elif current_row == 2: # 3x3 sp
                return game
            stdscr.getch()
            # if user selected last row, back the program
            if current_row == len(menu)-1:
                break

        print_menu(stdscr, current_row, menu)