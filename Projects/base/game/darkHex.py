from copy import deepcopy

from Projects.base.game.hex import Hex
from Projects.base.util.colors import colors

class DarkHex(Hex):
    def __init__(self, BOARD_SIZE=[3, 3], verbose=True,
                       custom_board_C_PLAYER1=[],
                       custom_board_C_PLAYER2=[]):
        '''
        Initializing a board. 

        args:
            BOARD_SIZE  - Size of the board, initially set to 3 by 3. [num_R, num_C]
        '''
        super().__init__(BOARD_SIZE=BOARD_SIZE, verbose=verbose)

        self.rev_color = {self.C_PLAYER2: self.C_PLAYER1, self.C_PLAYER1: self.C_PLAYER2}

        self.BOARDS = {self.C_PLAYER2: deepcopy(self.BOARD), self.C_PLAYER1: deepcopy(self.BOARD)}

        self.set_board(custom_board_C_PLAYER1, custom_board_C_PLAYER2)

        self.valid_moves_colors = {self.C_PLAYER2: deepcopy(self.valid_moves), self.C_PLAYER1: deepcopy(self.valid_moves)}
        self.move_history = {self.C_PLAYER1: [], self.C_PLAYER2: []}

    def rewind(self, passive=False):
        '''
        Rewinding the action given; removing the move made on the given position
        and adding the new empty position to the valid_moves.

        args:
            action    - The position to empty. In the format [row, column]
        '''
        last_move = None
        if passive:
            player = self.turn_info()
        else:
            player = self.rev_color[self.turn_info()]
        if not self.move_history[player]:
            return
        last_move = self.move_history[player].pop()
        if self.BOARDS[player][last_move] == player: # move was a success
            # fnuctional
            self.BOARD[last_move] = '.'
            self.valid_moves.add(last_move)
            
            # printing func
            self.cur_move_num -= 1
            self.game_history[last_move] =  '.'

        self.BOARDS[player][last_move] = '.'
        self.valid_moves_colors[player].add(last_move)

    def set_board(self, custom_board_C_PLAYER1, custom_board_C_PLAYER2):
        if custom_board_C_PLAYER1:
            self.BOARDS[self.C_PLAYER1] = [*custom_board_C_PLAYER1]
        if custom_board_C_PLAYER2:
            self.BOARDS[self.C_PLAYER2] = [*custom_board_C_PLAYER2]
        for i, (c1, c2) in enumerate(zip(self.BOARDS[self.C_PLAYER1], self.BOARDS[self.C_PLAYER2])):
            if c1 != c2 and not (c1 == '.' or c2 == '.'):
                # print('Invalid custom board sequence.')
                return False
            if c1 == self.C_PLAYER1:
                self.BOARD[i] = c1
            if c2 == self.C_PLAYER2:
                self.BOARD[i] = c2
        return True #success
            
    def print_information_set(self, player):
        if not self.verbose:
            print("Verbose is off, output is not shown.")
            return
        self.printBoard_for_player(player)
        print('Number of hidden {} stones: {}'\
               .format(self.rev_color[player], \
                       self.totalHidden_for_player(player)))

    def totalHidden_for_player(self, player):
        return self.BOARD.count(self.rev_color[player]) -\
               self.BOARDS[player].count(self.rev_color[player])
    
    def printBoard_for_player(self, player):
        '''
        Method for printing the board in a nice format.
        '''
        if not self.verbose:
            return
        print(colors.C_PLAYER1 + '  ' + '{0: <3}'.format(self.C_PLAYER1) * self.num_cols + colors.ENDC)
        print(colors.BOLD + colors.C_PLAYER1 + ' ' + '-' * (self.num_cols * 3 +1) + colors.ENDC)
        for cell in range(self.num_cells):
            if cell % self.num_cols == 0: # first col
                print(colors.BOLD + colors.C_PLAYER2 + self.C_PLAYER2 +'\\ ' + colors.ENDC, end= '')
            if self.BOARDS[player][cell] == self.C_PLAYER1:
                clr = colors.C_PLAYER1
            elif self.BOARDS[player][cell] == self.C_PLAYER2:
                clr = colors.C_PLAYER2
            else:
                clr = colors.NEUTRAL
            print(clr + '{0: <3}'.format(self.BOARDS[player][cell]) + colors.ENDC, end='') 
            if cell % self.num_cols == self.num_cols-1: # last col
                print(colors.BOLD + colors.C_PLAYER2 + '\\' + self.C_PLAYER2 + '\n' + (' ' * (cell//self.num_cols)) + colors.ENDC, end = ' ')
        print(colors.BOLD + colors.C_PLAYER1 + '  ' + '-' * (self.num_cols * 3 +1) + colors.ENDC)        
        print(colors.BOLD + colors.C_PLAYER1 + ' ' * (self.num_rows+4) + '{0: <3}'.format(self.C_PLAYER1) * self.num_cols + colors.ENDC)

    def step(self, color, action):
        '''
        Classic method to take a step, or make a move in the game. (Playing a stone
        on the board)

        args:
            color   - The color of the stone for the move being made.
            action  - The board position that the stone will be tried to place on.

        returns:
            Format >> [BOARD, done, result, reward]

            BOARD   - The current board position, state.
            done    - The truth value for if the game is over or not.
            result  - The winner of the game. If there is no winner yet (tie) returns
                    '=', otherwise returns the color that wins. The result returns 'f'
                    if the input given is invalid (If the move specified is illegal,
                    etc.).
            reward  - For the given player (color) if the current result is win the
                    reward is 1, if lose reward is -1 and 0 if it's a tie.
        '''
        if self.__placeStone(action, color):
            result = self.game_status()
        else:
            return 0, 0, 'f', 0
        
        if result == color:
            reward = 1
        elif result == '=':
            reward = 0
        else:
            reward = -1
        
        return self.BOARD, self.done, result, reward

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
        if self.BOARDS[color][cell] != '.':
            if self.verbose:
                print('Invalid Move.')
                print('Valid moves are:', self.valid_moves_colors[color])
            return False
        if self.BOARD[cell] != '.':
            self.BOARDS[color][cell] = self.rev_color[color]
            self.valid_moves_colors[color].remove(cell)
            self.move_history[color].append(cell)
            if self.verbose:
                print('This cell is taken.')
                print('Valid moves are:', self.valid_moves_colors[color])
                self.print_information_set(color)
            return False
        self.BOARD[cell] = color
        self.valid_moves.remove(cell)
        self.BOARDS[color][cell] = color
        self.valid_moves_colors[color].remove(cell)

        self.move_history[color].append(cell)

        self.game_history[cell] = color + str(self.cur_move_num)
        self.cur_move_num += 1
        return True

    def turn_info(self):
        '''
        Checks which players turn is it given the state and
        the number of hidden stones.
        
        Args:
            - state:    State to check the legality.
            - h:        Number of hidden stones.
        Returns:
            - C_PLAYER1/C_PLAYER2   Player whose turn it is.
        '''
        count_1 = self.BOARD.count(self.C_PLAYER1)
        count_2 = self.BOARD.count(self.C_PLAYER2)
        if count_1 <= count_2:
            return self.C_PLAYER1
        else:
            return self.C_PLAYER2