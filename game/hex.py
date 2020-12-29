# ...
#  ...
#   ...

#  black 
# 00 01 02        wh
#   10 11 12      i
#     20 21 22    te

#  EMPTY BOARD SIZE OF BOARD_SIZE

class HexBoard:
    '''
    Global:
        valid_moves     - All the valid moves in the current board. Essentially
                        the list of empty cells.
        done            - Boolean value for the game being done or not. If done,
                        there must be a winner as Hex is a no-draw game.
        BOARD           - Game board in x by y dimension
        BOARD_SIZE      - Size of the board
    '''

    def __init__(self, BOARD_SIZE=[3, 3], BOARD=None):
        '''
        Initializing a board. 

        args:
            BOARD_SIZE  - Size of the board, initially set to 3 by 3. [num_R, num_C]
            BOARD       - Predesigned board. Must be a list in x by y dimension.
                        This will overwrite the BOARD_SIZE to whatever dimension
                        the given board is.
        '''
        self.BOARD_SIZE = BOARD_SIZE

        if BOARD is None:
            self.BOARD = [['.' for __ in range(self.BOARD_SIZE[0])] for _ in range(self.BOARD_SIZE[1])]
        else:
            self.BOARD = BOARD
            self.BOARD_SIZE = [len(self.BOARD), len(self.BOARD[0])]

        self.valid_moves = [[i, j] for i in range(self.BOARD_SIZE[0]) for j in range(self.BOARD_SIZE[1])]
        self.done = False

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
            result = self.check_game_status()
        else:
            print('Valid moves are:', self.valid_moves)
            return 0, 0, 'f', 0
        
        # reward system: win +1 / loss -1
        self.valid_moves.remove(action)
        if result == color:
            reward = 1
        elif result == '=':
            reward = 0
        else:
            reward = -1
        
        return self.BOARD, self.done, result, reward

    def rewind(self, action):
        '''
        Rewinding the action given; removing the move made on the given position
        and adding the new empty position to the valid_moves.

        args:
            action    - The position to empty. In the format [row, column]
        '''
        self.BOARD[action[0]][action[1]] = '.'
        self.valid_moves.append(action)

    def printBoard(self):
        '''
        Method for printing the board in a nice format.
        '''
        for i in range(self.BOARD_SIZE[0]):
            print('  '*(self.BOARD_SIZE[0]-i-1), end='')
            for j in range(self.BOARD_SIZE[1]):
                print(self.BOARD[i][j], end=' ')
            print('')

    def __checkEdge(self, color, node):
        '''
        Checks if the given node is the edge node for the given color.

        args:
            color   - The color of the player to check the edge for.
            node    - The location on the board we check if its the edge
                    for the given player or not.
        
        returns:
            format >> True/False

            True/False  - True if end of the board for given color 
                        False if not
        '''
        if color == 'W' and node[1] == self.BOARD_SIZE[1]-1:
            return True
        if color == 'B' and node[0] == self.BOARD_SIZE[0]-1:
            return True
        return False

    def __testConnections(self, cellToCheck):
        '''
        Testing the connections for a given cell.
        '''
        print('connections are', self.cell_connections(cellToCheck))

    def __placeStone(self, cell, color):
        '''
        Placing a stone on the given board location.

        args:
            cell    - The location on the board to place the stone.
                    In the format [row, column]
            color   - The color of the stone.
        
        returns:
            True if the action was valid, and false otherwise.
        '''
        if self.BOARD[cell[0]][cell[1]] != '.':
            print('Invalid Action Attempted')
            return False
        self.BOARD[cell[0]][cell[1]] = color
        return True

    def __cell_connections(self, cell):
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
        row = cell[0]
        col = cell[1]

        positions = []
        1, 1
        3, 3
        if col + 1 < self.BOARD_SIZE[1]:
            positions.append([row, col + 1])
        if col - 1 >= 0:
            positions.append([row, col - 1])
        if row + 1 < self.BOARD_SIZE[0]:
            positions.append([row + 1, col])
            if col - 1 >= 0:
                positions.append([row + 1, col - 1])
        if row - 1 >= 0:
            positions.append([row - 1, col])
            if col + 1 < self.BOARD_SIZE[1]:
                positions.append([row - 1, col + 1])
        
        return positions
    
    def check_game_status(self):
        '''
        Checks the game status by looking at the board and determining the winning player if any, returning
        the winner, or '=' if there is no winner.

        returns:
            format >> 'W'/'B'/'='

            'W'/'B'/'=' - winner is white/black or its a tie ('=')
        '''
        # checking for white
        self.CHECK_BOARD = [[False for _ in range(self.BOARD_SIZE[0])] for _ in range(self.BOARD_SIZE[1])] 
        for i in range(self.BOARD_SIZE[0]):
            if self.BOARD[i][0] == 'W':
                self.CHECK_BOARD[i][0] = True
                self.__check_connections(self.__cell_connections([i, 0]), 'W')
                if self.done:
                    self.done = False
                    return 'W'
        # checking for black
        self.CHECK_BOARD = [[False for _ in range(self.BOARD_SIZE[0])] for _ in range(self.BOARD_SIZE[1])] 
        for i in range(self.BOARD_SIZE[1]):
            if self.BOARD[0][i] == 'B':
                self.CHECK_BOARD[0][i] = True

                self.__check_connections(self.__cell_connections([0, i]), 'B')
                if self.done:
                    self.done = False
                    return 'B'
        return '=' 

    def __check_connections(self, connections, color):
        '''
        Checking and following all the given connections for the given color, and changes the done status
        to the winner if finds a connection to the edge of the board.

        args:
            connections - The connections to follow for searching the end edge.
            color       - The color to check the connections for
        '''
        for c in connections:
            row = c[0]
            col = c[1]
            if self.BOARD[row][col] == color and not self.CHECK_BOARD[row][col]:
                # print(row, col, 'visited')
                if self.__checkEdge(color, c):
                    self.done = True
                    return
                self.CHECK_BOARD[row][col] = True
                self.__check_connections(self.__cell_connections([row, col]), color)