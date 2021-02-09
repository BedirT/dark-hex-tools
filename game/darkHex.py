from copy import deepcopy

from game.Hex import Hex

class DarkHex(Hex):

    def __init__(self, BOARD_SIZE=[3, 3]):
        '''
        Initializing a board. 

        args:
            BOARD_SIZE  - Size of the board, initially set to 3 by 3. [num_R, num_C]
        '''
        super().__init__(BOARD_SIZE=BOARD_SIZE)

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
        self.BOARD[action[0]][action[1]] = '.'
        self.valid_moves.append(action)

        self.BOARDS['B'][action[0]][action[1]] = '.'
        self.valid_moves_colors['B'].append(action)

        self.BOARDS['W'][action[0]][action[1]] = '.'
        self.valid_moves_colors['W'].append(action)

    def printBoard_for_player(self, player):
        '''
        Method for printing the players visible board in a nice format.
        '''

        for i in range(self.BOARD_SIZE[0]):
            print(' '*i, end='')
            for j in range(self.BOARD_SIZE[1]):
                print(self.BOARDS[player][i][j], end=' ')
            print('')

    def __placeStone(self, cell, color):
        '''
        Placing a stone on the given board location for the main board and 
        the board for player -color-. If the move is invalid (there is a
        stone already placed in the location provided) the function will
        return False, otherwise make the move and return True.

        args:
            cell    - The location on the board to place the stone.
                    In the format [row, column]
            color   - The color of the stone.
        
        returns:
            True if the action was valid, and false otherwise.
        '''
        if self.BOARDS[color][cell[0]][cell[1]] != '.':
            print('Invalid Move.')
            return False
        if self.BOARD[cell[0]][cell[1]] != '.':
            print('This cell is taken.')
            self.BOARDS[color][cell[0]][cell[1]] = self.rev_color[color]
            return False
        self.BOARD[cell[0]][cell[1]] = color
        self.valid_moves.remove(cell)
        self.BOARDS[color][cell[0]][cell[1]] = color
        self.valid_moves_colors[color].remove(cell)
        return True