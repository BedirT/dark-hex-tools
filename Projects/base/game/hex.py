# ...
#  ...
#   ...

#  black 
#   0 1 2      wh
#    3 4 5     i
#     6 7 8    te

#  EMPTY BOARD SIZE OF BOARD_SIZE

from Projects.base.util.colors import colors
from collections import Counter

class pieces:
    # open_spiel states being used.
    kEmpty = '.'
    kWhite = 'o'
    kWhiteWin = 'O'
    kBlack = 'x'
    kBlackWin = 'X'
    kWhiteWest = 'p'
    kWhiteEast = 'q'
    kBlackNorth = 'y'
    kBlackSouth = 'z'
    # Additions
    kDraw = '='
    kFail = 'f'
    kIllegal = 'i'
    # Piece sets
    black_pieces = [kBlack, kBlackWin, kBlackNorth, kBlackSouth]
    white_pieces = [kWhite, kWhiteWin, kWhiteWest, kWhiteEast]

class Hex:
    '''
    valid_moves     - All the valid moves in the current board. Essentially
                    the list of empty cells.
    done            - Boolean value for the game being done or not. If done,
                    there must be a winner as Hex is a no-draw game.
    BOARD           - Game board in x by y dimension
    BOARD_SIZE      - Size of the board
    '''

    def __init__(self, BOARD_SIZE=[3, 3], BOARD=None, 
                 verbose=True, legality_check=False,
                 early_w_p1=False, early_w_p2=False, h=0,
                 h_player=None):
        '''
        Initializing a board. 

        args:
            BOARD_SIZE  - Size of the board, initially set to 3 by 3. [r, c]
            BOARD       - Predesigned board. An array of size r x c
        '''
        self.num_rows = BOARD_SIZE[0]
        self.num_cols = BOARD_SIZE[1]
        self.num_cells = self.num_rows * self.num_cols
        self.rev_color = {pieces.kWhite: pieces.kBlack, pieces.kBlack: pieces.kWhite}

        # to print game as a history
        self.game_history_str = [pieces.kEmpty] * self.num_cells
        self.cur_move_num = 1

        if BOARD:
            self.BOARD = BOARD
            self.__init_custom_board()
        else:
            self.BOARD = [pieces.kEmpty] * self.num_cells
            self.valid_moves = set(range(self.num_cells))
            self.turn_info = pieces.kBlack
            self.game_length = 0

        # keep everything quiet/not
        self.verbose = verbose

        # check if the board is legal
        # if asked to do so. For some research questions we do
        # not want to check the validity of the board, therefor
        # we set the legality_check to false.
        #### Mostly used for pONE algorithm.
        self.legality_check = legality_check
        self.early_w_p1 = early_w_p1
        self.early_w_p2 = early_w_p2
        self.h = h; self.h_player = h_player

    def __init_custom_board(self):
        '''
        Initializing the custom board for the game.
        '''
        # update valid moves
        self.valid_moves = set(range(self.num_cells))
        # set the turn info
        self.turn_info = self.__turn_info()  
        # set the game length
        self.game_length = self.num_cells - len(self.valid_moves)

    def step(self, color, action):
        '''
        Classic method to take a step, or make a move in the game. (Playing a stone
        on the board)

        args:
            color       - The color of the player making the move.
            action      - The board position that the stone will be tried to place on. (int)

        returns:
            Format >> [BOARD, result, reward]

            BOARD       - The new BOARD after the move is made.
            result      - The result of the move. Either '=' for draw, 'W' for white win,
                        'B' for black win, or 'i' for illegal state.
            reward      - The reward for the move.
        '''
        if self.legality_check:
            if not self.check_legal():
                return 0, pieces.kIllegal, 0
        move = self.__placeStone(action, color)
        if  move == pieces.kBlackWin:
            result = pieces.kBlack
        elif move == pieces.kWhiteWin:
            result = pieces.kWhite
        elif move: 
            result = pieces.kDraw
        else:
            if self.verbose:
                print('Valid moves are:', self.valid_moves)
            return 0, pieces.kFail, 0
        
        if result == color:
            reward = 1
        elif result == pieces.kDraw:
            reward = 0
        else:
            reward = -1
        
        return self.BOARD, result, reward

    def rewind(self, cell=None):
        '''
        Rewinds the game board to the previous state. If a cell is specified,
        rewinds that cell to the previous state (empty).
        '''
        self.game_length -= 1
        self.turn_info = self.rev_color[self.turn_info]
        if cell:
            self.BOARD[cell] = pieces.kEmpty
            self.valid_moves.append(cell)
        else:
            # ! implement rewind the last move
            Exception('Must specify a cell to rewind. This functionality is not implemented yet.')

    def printBoard(self):
        '''
        Method for printing the board in a nice format.
        '''
        if not self.verbose:
            print("Verbose is off, output is not shown.")
            return
        if self.game_history_str.count(pieces.kEmpty) != self.BOARD.count(pieces.kEmpty):
            for x in range(len(self.game_history_str)):
                self.game_history_str[x] = self.BOARD[x] + '0' if self.BOARD[x] != pieces.kEmpty else pieces.kEmpty
        print(colors.C_PLAYER1 + '  ' + '{0: <3}'.format(pieces.kBlack) * self.num_cols + colors.ENDC)
        print(colors.BOLD + colors.C_PLAYER1 + ' ' + '-' * (self.num_cols * 3 +1) + colors.ENDC)
        for cell in range(self.num_cells):
            if cell % self.num_cols == 0: # first col
                print(colors.BOLD + colors.C_PLAYER2 + pieces.kWhite + '\\ ' + colors.ENDC, end= '')
            if self.game_history_str[cell][0] in [pieces.kBlack, pieces.kBlackWin, pieces.kBlackNorth, pieces.kBlackSouth]:
                clr = colors.C_PLAYER1
            elif self.game_history_str[cell][0] in [pieces.kWhite, pieces.kWhiteEast, pieces.kWhiteWest, pieces.kWhiteWin]:
                clr = colors.C_PLAYER2
            else:
                clr = colors.NEUTRAL
            print(clr + '{0: <3}'.format(self.game_history_str[cell]) + colors.ENDC, end='') 
            if cell % self.num_cols == self.num_cols-1: # last col
                print(colors.BOLD + colors.C_PLAYER2 + '\\' + pieces.kWhite + '\n' + (' ' * (cell//self.num_cols)) + colors.ENDC, end = ' ')
        print(colors.BOLD + colors.C_PLAYER1 + '  ' + '-' * (self.num_cols * 3 +1) + colors.ENDC)        
        print(colors.BOLD + colors.C_PLAYER1 + ' ' * (self.num_rows+4) + '{0: <3}'.format(pieces.kBlack) * self.num_cols + colors.ENDC)

    def __find_row(self, node):
        return node // self.num_cols

    def __find_col(self, node):
        return node % self.num_cols

    def __pos_by_coord(self, r, c):
        return self.num_cols * r + c

    def __placeStone(self, cell, color):
        '''
        Placing a stone on the given board location.

        args:
            cell    - The location on the board to place the stone.
                    In the format (int)
            color   - The color of the stone.
        
        returns:
            True if the action was valid, and false otherwise.
        '''
        if self.BOARD[cell] != pieces.kEmpty:
            if self.verbose:
                print('Invalid Action Attempted')
            return False
        if color == pieces.kBlack:
            north_connected = False
            south_connected = False 
            if cell < self.num_cols: # First row
                north_connected = True
            elif cell >= self.num_cols * (self.num_rows - 1): # Last row
                south_connected = True
            for neighbour in self._cell_connections(cell):
                if self.BOARD[neighbour] == pieces.kBlackNorth:
                    north_connected = True
                elif self.BOARD[neighbour] == pieces.kBlackSouth:
                    south_connected = True
            if north_connected and south_connected:
                self.BOARD[cell] = pieces.kBlackWin
            elif north_connected:
                self.BOARD[cell] = pieces.kBlackNorth
            elif south_connected:
                self.BOARD[cell] = pieces.kBlackSouth
            else:
                self.BOARD[cell] = pieces.kBlack
        elif color == pieces.kWhite:
            east_connected = False
            west_connected = False
            if cell % self.num_cols == 0: # First column
                west_connected = True
            elif cell % self.num_cols == self.num_cols - 1: # Last column
                east_connected = True
            for neighbour in self._cell_connections(cell):
                if self.BOARD[neighbour] == pieces.kWhiteWest:
                    west_connected = True
                elif self.BOARD[neighbour] == pieces.kWhiteEast:
                    east_connected = True
            if east_connected and west_connected:
                self.BOARD[cell] = pieces.kWhiteWin
            elif east_connected:
                self.BOARD[cell] = pieces.kWhiteEast
            elif west_connected:
                self.BOARD[cell] = pieces.kWhiteWest
            else:
                self.BOARD[cell] = pieces.kWhite
        self.valid_moves.remove(cell)
        self.game_length += 1
        self.turn_info = self.rev_color[color]
        if self.BOARD[cell] in [pieces.kBlackWin, pieces.kWhiteWin]:
            return self.BOARD[cell]
        elif self.BOARD[cell] not in [pieces.kBlack, pieces.kWhite]:
            # The cell is connected to an edge but not a win position.
            # We need to use flood-fill to find the connected edges.
            flood_stack = [cell]
            latest_cell = 0
            while len(flood_stack) != 0:
                latest_cell = flood_stack.pop()
                for neighbour in self._cell_connections(latest_cell):
                    if self.BOARD[neighbour] == color:
                        self.BOARD[neighbour] = self.BOARD[cell]
                        flood_stack.append(neighbour)
            # Flood-fill is complete.
        # ! Decide if u wanna change this
        self.game_history_str[cell] = color + str(self.cur_move_num)
        self.cur_move_num += 1
        return True

    def _game_status(self):
        '''
        Checks the current game status and returns the appropriete
        string. Checks if the board has a kBlackWin or kWhiteWin.

        Return:
            kBlackWin  - Black wins
            kWhiteWin  - White wins
            kDraw      - Draw 
        '''
        ct = Counter(self.BOARD)
        if ct[pieces.kBlackWin] > 0:
            return pieces.kBlackWin
        elif ct[pieces.kWhiteWin] > 0:
            return pieces.kWhiteWin
        else:
            return pieces.kDraw
          
    def _cell_connections(self, cell):
        '''
        Returns the neighbours of the given cell.

        args:
            cell    - The location on the board to check the neighboring cells for.
                    In the format [row, column]
        
        returns:
            format >> positions

            positions   - List of all the neighbouring cells to the cell.
                        Elements are in the format [row, column].
        '''
        row = self.__find_row(cell)
        col = self.__find_col(cell)

        positions = []
        if col + 1 < self.num_cols:
            positions.append(self.__pos_by_coord(row, col + 1))
        if col - 1 >= 0:
            positions.append(self.__pos_by_coord(row, col - 1))
        if row + 1 < self.num_rows:
            positions.append(self.__pos_by_coord(row + 1, col))
            if col - 1 >= 0:
                positions.append(self.__pos_by_coord(row + 1, col - 1))
        if row - 1 >= 0:
            positions.append(self.__pos_by_coord(row - 1, col))
            if col + 1 < self.num_cols:
                positions.append(self.__pos_by_coord(row - 1, col + 1))
        return positions

    def check_legal(self):
        # number of the stones are illegal
        ct = Counter(self.BOARD)
        # get the white pieces from ct counter using pieces
        count_white = ct[pieces.kWhite] + ct[pieces.kWhiteEast] + ct[pieces.kWhiteWin] + ct[pieces.kWhiteWest]
        # get the black pieces from ct counter using pieces
        count_black = ct[pieces.kBlack] + ct[pieces.kBlackNorth] + ct[pieces.kBlackWin] + ct[pieces.kBlackSouth]
        if self.h_player == pieces.kBlack:
            count_black += self.h
        else:
            count_white += self.h
        if (count_black + count_white > self.num_cells) or \
           (count_black - count_white > 1 or count_white > count_black):
            return False
        
        # white wins with removing a white stone
        if self.early_w_p2 and self.check_early_win(pieces.kWhite):
            return False
        # black wins with removing a black stone
        if self.early_w_p1 and self.check_early_win(pieces.kBlack):
            return False

        return True
        
    def check_early_win(self, color):
        '''
        Returns false if any of the moves is not resulting with a win.

        The game should be win for any stone removed in color, to be
        a definite early win
        '''
        if color == pieces.kBlack:
            color_set = [pieces.kBlack, pieces.kBlackNorth, pieces.kBlackWin, pieces.kBlackSouth]
        else:
            color_set = [pieces.kWhite, pieces.kWhiteEast, pieces.kWhiteWin, pieces.kWhiteWest]
        for c in range(len(self.BOARD)):
            if self.BOARD[c] not in color_set:
                continue
            temp = self.BOARD[c]
            self.BOARD[c] = pieces.kEmpty; self.legality_check = False
            self.__placeStone(c, color)
            res = self.game_status()
            self.BOARD[c] = temp; self.legality_check = True
            if res != color:
                return False
        return True  

    def __turn_info(self):
        '''
        Only used for custom boards.
        Initializes the board turn information, save it to the
        turn_info variable. Do not use this function exterally.

        Returns:
            - Player whose turn it is using pieces.
        '''
        ct = Counter(self.BOARD)
        # get the white pieces from ct counter using pieces
        count_white = ct[pieces.kWhite] + ct[pieces.kWhiteEast] + ct[pieces.kWhiteWin] + ct[pieces.kWhiteWest]
        # get the black pieces from ct counter using pieces
        count_black = ct[pieces.kBlack] + ct[pieces.kBlackNorth] + ct[pieces.kBlackWin] + ct[pieces.kBlackSouth]
        if count_black <= count_white:
            return pieces.kBlack
        else:
            return pieces.kWhite

def customBoard_print(board, num_cols, num_rows):
    '''
    Method for printing the board in a nice format.
    '''
    num_cells = num_cols * num_rows
    print(colors.C_PLAYER1 + '  ' + '{0: <3}'.format(pieces.kBlack) * num_cols + colors.ENDC)
    print(colors.BOLD + colors.C_PLAYER1 + ' ' + '-' * (num_cols * 3 +1) + colors.ENDC)
    for cell in range(num_cells):
        if cell % num_cols == 0: # first col
            print(colors.BOLD + colors.C_PLAYER2 + pieces.kWhite + '\ ' + colors.ENDC, end= '')
        if board[cell] in pieces.black_pieces:
            clr = colors.C_PLAYER1
        elif board[cell] in pieces.white_pieces:
            clr = colors.C_PLAYER2
        else:
            clr = colors.NEUTRAL
        print(clr + '{0: <3}'.format(board[cell]) + colors.ENDC, end='') 
        if cell % num_cols == num_cols-1: # last col
            print(colors.BOLD + colors.C_PLAYER2 + '\\' + pieces.kWhite + '\n' + (' ' * (cell//num_cols)) + colors.ENDC, end = ' ')
    print(colors.BOLD + colors.C_PLAYER1 + '  ' + '-' * (num_cols * 3 +1) + colors.ENDC)        
    print(colors.BOLD + colors.C_PLAYER1 + ' ' * (num_rows+4) + '{0: <3}'.format(pieces.kBlack) * num_cols + colors.ENDC)

def print_init_board(num_cols, num_rows):
    '''
    Print the board numbers
    '''
    num_cells = num_cols * num_rows
    print(colors.C_PLAYER1 + '  ' + '{0: <3}'.format(pieces.kBlack) * num_cols + colors.ENDC)
    print(colors.BOLD + colors.C_PLAYER1 + ' ' + '-' * (num_cols * 3 +1) + colors.ENDC)
    for cell in range(num_cells):
        if cell % num_cols == 0: # first col
            print(colors.BOLD + colors.C_PLAYER2 + pieces.kWhite + '\ ' + colors.ENDC, end= '')
        print(colors.NEUTRAL + '{0: <3}'.format(cell) + colors.ENDC, end='') 
        if cell % num_cols == num_cols-1: # last col
            print(colors.BOLD + colors.C_PLAYER2 + '\\' + pieces.kWhite + '\n' + (' ' * (cell//num_cols)) + colors.ENDC, end = ' ')
    print(colors.BOLD + colors.C_PLAYER1 + '  ' + '-' * (num_cols * 3 +1) + colors.ENDC)        
    print(colors.BOLD + colors.C_PLAYER1 + ' ' * (num_rows+4) + '{0: <3}'.format(pieces.kBlack) * num_cols + colors.ENDC)
    
def multiBoard_print(board1, board2, num_rows, num_cols, title1='', title2=''):
    '''
    Method for printing the board in a nice format.
    '''
    num_cells = num_cols * num_rows
    gap = "{0:^10}".format(' ')
    s = ''
    if title1 != '' or title2 != '':
        s += colors.BOLD + '  {}{}       {}\n'.format(title1,gap,title2) + colors.ENDC
    s += colors.C_PLAYER1 + '  ' + '{0: <3}'.format(pieces.kBlack) * num_cols + colors.ENDC
    s += gap
    s += colors.C_PLAYER1 + '     ' + '{0: <3}'.format(pieces.kBlack) * num_cols + colors.ENDC + '\n'
    s += colors.C_PLAYER1 + ' ' + '-' * (num_cols * 3 +1) + colors.ENDC
    s += gap
    s += colors.C_PLAYER1 + '    ' + '-' * (num_cols * 3 +1) + colors.ENDC + '\n'
    
    for cell in range(num_cells):
        if cell % num_cols == 0: # first col
            s1 = colors.BOLD + colors.C_PLAYER2 + pieces.kWhite + '\ ' + colors.ENDC
            s2 = colors.BOLD + colors.C_PLAYER2 + pieces.kWhite + '\ ' + colors.ENDC
        
        if board1[cell] in pieces.black_pieces:     clr1 = colors.C_PLAYER1
        elif board1[cell] in pieces.white_pieces:   clr1 = colors.C_PLAYER2
        else: clr1 = colors.NEUTRAL
        
        if board2[cell] in pieces.black_pieces:     clr2 = colors.C_PLAYER1
        elif board2[cell] in pieces.white_pieces:   clr2 = colors.C_PLAYER2
        else: clr2 = colors.NEUTRAL
        
        s1 += clr1 + '{0: <3}'.format(board1[cell]) + colors.ENDC
        s2 += clr2 + '{0: <3}'.format(board2[cell]) + colors.ENDC
        
        if cell % num_cols == num_cols-1: # last col
            s1 += colors.BOLD + colors.C_PLAYER2 + '\\' + pieces.kWhite
            s2 += colors.BOLD + colors.C_PLAYER2 + '\\' + pieces.kWhite
            s2 += '\n' + (' ' * (cell//num_cols)) + ' ' + colors.ENDC
            
            s += s1 + gap + s2
            
    s += colors.BOLD + colors.C_PLAYER1 + '  ' + '-' * (num_cols * 3 +1) + colors.ENDC
    s += gap
    s += colors.BOLD + colors.C_PLAYER1 + '    ' + '-' * (num_cols * 3 +1) + colors.ENDC + '\n'
    s += colors.BOLD + colors.C_PLAYER1 + ' ' * (num_rows+4) + '{0: <3}'.format(pieces.kBlack) * num_cols + colors.ENDC
    s += gap
    s += colors.BOLD + colors.C_PLAYER1 + ' ' * (num_rows+2) + '{0: <3}'.format(pieces.kBlack) * num_cols + colors.ENDC + '\n'
    
    print(s)
    
# multiBoard_print('...x...x.', 'xxo......', 3, 3, 'Board 1', 'Board 2')