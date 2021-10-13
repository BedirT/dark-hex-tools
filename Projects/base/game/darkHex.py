from collections import Counter
from copy import deepcopy

from Projects.base.game.hex import Hex, pieces
from Projects.base.util.colors import colors

class DarkHex(Hex):
    def __init__(self, BOARD_SIZE=[3, 3], verbose=True,
                       custom_board_p1=[],
                       custom_board_p2=[]):
        '''
        Initializing a board. 

        args:
            BOARD_SIZE  - Size of the board, initially set to 3 by 3. [num_R, num_C]
        '''
        super().__init__(BOARD_SIZE=BOARD_SIZE, verbose=verbose)

        # Set up the game for the two players in imperfect information setting
        self.BOARDS = {pieces.kBlack: deepcopy(self.BOARD), pieces.kWhite: deepcopy(self.BOARD)}
        self.valid_moves_colors = {pieces.kBlack: deepcopy(self.valid_moves), pieces.kWhite: deepcopy(self.valid_moves)}
        self.move_history = {pieces.kBlack: [], pieces.kWhite: []}
        self.all_move_history = []
        self.hidden_stones = {pieces.kBlack: 0, pieces.kWhite: 0}

        # self.__set_board(custom_board_p1, custom_board_p2)

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

    def rewind(self):
        '''
        Rewinds the game to the previous state.
        '''
        if not self.all_move_history:
            # If the player didn't make any move, then we need to rewind to the
            # rewind fails, no action is required.
            return
        player, last_move = self.all_move_history.pop()
        if self.get_player(self.BOARDS[player][last_move]) == player: # move was a success
            # empty the cell and update valid moves
            self.BOARD[last_move] = pieces.kEmpty
            self.valid_moves.add(last_move)
            # self.turn_info = self.rev_color[player]
            
            # printing func
            self.cur_move_num -= 1
            self.game_history_str[last_move] = pieces.kEmpty
        else:
            self.hidden_stones[player] -= 1

        self.game_length -= 1
        self.BOARDS[player][last_move] = pieces.kEmpty
        self.valid_moves_colors[player].add(last_move)
    
    def get_player(self, piece):
        '''
        Returns the player that the piece belongs to.
        '''
        if piece in pieces.black_pieces:
            return pieces.kBlack
        elif piece in pieces.white_pieces:
            return pieces.kWhite
        else:
            return None

    def turn_information_func(self):
        '''
        Returns which player has the next move.
        '''
        ctboard = Counter(self.BOARD)
        # black pieces
        ct_black = ctboard[pieces.kBlack] + ctboard[pieces.kBlackNorth] + ctboard[pieces.kBlackWin] + \
                   ctboard[pieces.kBlackSouth]
        # white pieces
        ct_white = ctboard[pieces.kWhite] + ctboard[pieces.kWhiteEast] + ctboard[pieces.kWhiteWin] + \
                   ctboard[pieces.kWhiteWest]
        return  (pieces.kBlack if ct_black <= ct_white else pieces.kWhite)

    def __set_board(self, custom_board_p1, custom_board_p2):
        '''
        Sets the board to the custom board provided, if the custom boards are
        valid. Otherwise, the board is set to the default one.
        '''
        if custom_board_p1 and custom_board_p2:
            self.BOARDS[pieces.kBlack] = custom_board_p1
            self.BOARDS[pieces.kWhite] = custom_board_p2
        else:
            Exception('Invalid custom boards provided!')
            return
        for i, (c1, c2) in enumerate(zip(custom_board_p1, custom_board_p2)):
            if c1 != c2 and not (c1 == pieces.kEmpty or c2 == pieces.kEmpty):
                Exception(f'Invalid custom board at index {i}')
                return
            if c1 == pieces.kBlack:
                self.BOARD[i] = c1
            if c2 == pieces.kWhite:
                self.BOARD[i] = c2
        self.hidden_stones[pieces.kBlack] = self.BOARD.count(pieces.kWhite) \
                                            - self.BOARDS[pieces.kBlack].count(
                                                  self.rev_color[pieces.kWhite])
        self.hidden_stones[pieces.kWhite] = self.BOARD.count(pieces.kBlack) \
                                            - self.BOARDS[pieces.kWhite].count(
                                                  self.rev_color[pieces.kBlack])

    # ! USE A VARIABLE INSTEAD
    # Cant seem to fix
    def hidden_stones_count(self, player):
        ctboard = Counter(self.BOARD)
        if player == pieces.kBlack:
            ctboard_p = Counter(self.BOARDS[player])
            boardcount = ctboard[pieces.kWhite] + ctboard[pieces.kWhiteEast] + ctboard[pieces.kWhiteWin] + \
                   ctboard[pieces.kWhiteWest] 
            boardcount_p = ctboard_p[pieces.kWhite] + ctboard_p[pieces.kWhiteEast] + ctboard_p[pieces.kWhiteWin] + \
                   ctboard_p[pieces.kWhiteWest]
        else:
            ctboard_p = Counter(self.BOARDS[player])
            boardcount = ctboard[pieces.kBlack] + ctboard[pieces.kBlackNorth] + ctboard[pieces.kBlackWin] + \
                   ctboard[pieces.kBlackSouth]
            boardcount_p = ctboard_p[pieces.kBlack] + ctboard_p[pieces.kBlackNorth] + ctboard_p[pieces.kBlackWin] + \
                   ctboard_p[pieces.kBlackSouth]
        return boardcount - boardcount_p
          
    def print_information_set(self, player):
        if not self.verbose:
            print("Verbose is off, output is not shown.")
            return
        self.printBoard_for_player(player)
        print('Number of hidden {} stones: {}'\
               .format(self.rev_color[player], \
                       self.hidden_stones[player]))

    def printBoard_for_player(self, player):
        '''
        Method for printing the board in a nice format.
        '''
        if not self.verbose:
            return
        print(colors.C_PLAYER1 + '  ' + '{0: <3}'.format(pieces.kBlack) * self.num_cols + colors.ENDC)
        print(colors.BOLD + colors.C_PLAYER1 + ' ' + '-' * (self.num_cols * 3 +1) + colors.ENDC)
        for cell in range(self.num_cells):
            if cell % self.num_cols == 0: # first col
                print(colors.BOLD + colors.C_PLAYER2 + pieces.kWhite +'\\ ' + colors.ENDC, end= '')
            if self.BOARDS[player][cell] == pieces.kBlack:
                clr = colors.C_PLAYER1
            elif self.BOARDS[player][cell] == pieces.kWhite:
                clr = colors.C_PLAYER2
            else:
                clr = colors.NEUTRAL
            print(clr + '{0: <3}'.format(self.BOARDS[player][cell]) + colors.ENDC, end='') 
            if cell % self.num_cols == self.num_cols-1: # last col
                print(colors.BOLD + colors.C_PLAYER2 + '\\' + pieces.kWhite + '\n' + (' ' * (cell//self.num_cols)) + colors.ENDC, end = ' ')
        print(colors.BOLD + colors.C_PLAYER1 + '  ' + '-' * (self.num_cols * 3 +1) + colors.ENDC)        
        print(colors.BOLD + colors.C_PLAYER1 + ' ' * (self.num_rows+4) + '{0: <3}'.format(pieces.kBlack) * self.num_cols + colors.ENDC)

    def get_information_set(self, player):
        '''
        Returns the information set of the player as a string.
        '''
        return ''.join(self.BOARDS[player]) + str(self.hidden_stones_count(player))

    def __placeStone(self, cell, color):
        '''
        Placing a stone on the given board location for the main board and 
        the board for player -color-. If the move is invalid (there is a
        stone already placed in the location provided) the function will
        return False, otherwise make the move and return True.

        args:
            cell    - The location on the board to place the stone.
                      int format
            color   - The color of the stone.
        
        returns:
            True if the action was valid, and false otherwise.
        '''
        # Check if the move is valid
        if self.BOARDS[color][cell] != pieces.kEmpty:
            if self.verbose:
                print('Invalid Move.')
                print('Valid moves are:', self.valid_moves_colors[color])
            return False
        self.game_length += 1
        self.move_history[color].append(cell)
        self.all_move_history.append((color, cell))
        # Check if the cell is already occupied
        if self.BOARD[cell] != pieces.kEmpty:
            self.BOARDS[color][cell] = self.rev_color[color]
            self.valid_moves_colors[color].remove(cell)
            if self.verbose:
                print('This cell is taken.')
                print('Valid moves are:', self.valid_moves_colors[color])
                self.print_information_set(color)
            return False
        if color == pieces.kBlack:
            north_connected = False
            south_connected = False 
            if self.num_rows == 1: # There is only one row so first & last row
                north_connected = True
                south_connected = True
            elif cell < self.num_cols: # First row
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
            if self.num_cols == 1: # There is only one col so first & last col
                east_connected = True
                west_connected = True
            elif cell % self.num_cols == 0: # First column
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
        self.BOARDS[color][cell] = self.BOARD[cell]

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
        self.valid_moves.remove(cell)
        # self.turn_info = self.rev_color[color]
        self.valid_moves_colors[color].remove(cell)

        self.game_history_str[cell] = color + str(self.cur_move_num)
        self.cur_move_num += 1
        return True