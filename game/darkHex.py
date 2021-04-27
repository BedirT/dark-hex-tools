from copy import deepcopy

from game.hex import Hex

class DarkHex(Hex):

    def __init__(self, BOARD_SIZE=[3, 3], verbose=True):
        '''
        Initializing a board. 

        args:
            BOARD_SIZE  - Size of the board, initially set to 3 by 3. [num_R, num_C]
        '''
        super().__init__(BOARD_SIZE=BOARD_SIZE, verbose=verbose)

        self.rev_color = {'W': 'B', 'B': 'W'}

        self.BOARDS = {'W': deepcopy(self.BOARD), 'B': deepcopy(self.BOARD)}

        self.valid_moves_colors = {'W': deepcopy(self.valid_moves), 'B': deepcopy(self.valid_moves)}

    def rewind(self, action):
        '''
        Rewinding the action given; removing the move made on the given position
        and adding the new empty position to the valid_moves.

        args:
            action    - The position to empty. In the format [row, column]
        '''
        self.BOARD[action] = '.'
        self.valid_moves.append(action)

        self.BOARDS['B'][action] = '.'
        self.valid_moves_colors['B'].append(action)

        self.BOARDS['W'][action] = '.'
        self.valid_moves_colors['W'].append(action)

    def printBoard_for_player(self, player):
        '''
        Method for printing the players visible board in a nice format.
        '''
        if not self.verbose:
            print("Verbose is off, output is not shown.")
            return
        for cell in range(self.num_cells):
            print(self.BOARDS[player][cell], end=' ') 
            if cell % self.num_cols == self.num_cols-1: # last col
                print('\n' + (' ' * (cell//self.num_cols)), end = ' ')
        print()

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
            if self.verbose:
                print('This cell is taken.')
                print('Valid moves are here:', self.valid_moves_colors[color])
            return False
        self.BOARD[cell] = color
        self.valid_moves.remove(cell)
        self.BOARDS[color][cell] = color
        self.valid_moves_colors[color].remove(cell)
        return True