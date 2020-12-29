#   ...
#  ...
# ...

#       black 
#     00 01 02  wh
#   10 11 12    i
# 20 21 22      te

#  EMPTY BOARD SIZE OF BOARD_SIZE

class HexBoard:
    def __init__(self, BOARD_SIZE=[3, 3], BOARD=None):
        self.BOARD_SIZE = BOARD_SIZE
        if BOARD is None:
            self.BOARD = [['.' for __ in range(self.BOARD_SIZE[0])] for _ in range(self.BOARD_SIZE[1])]
        else:
            self.BOARD = BOARD
        self.valid_moves = [[i, j] for i in range(self.BOARD_SIZE[0]) for j in range(self.BOARD_SIZE[1])]
        self.done = False # game is over or not

    def step(self, color, action):
        # color = 'B' or 'W'
        # action = [x, y]
        try:
            input_err = self.placeStone(action, color) 
                # False if there is an error in the input
            result = self.check_game_status()
        except Exception:
            # print('Valid moves are:', self.valid_moves)
            return 0, 0, 0, 0, False
        # reward system: win +1 / loss -1
        self.valid_moves.remove(action)
        if result == color:
            reward = 1
        elif result == '=':
            reward = 0
        else:
            reward = -1
        return self.BOARD, self.done, result, reward, input_err

    def rewind(self, action):
        self.BOARD[action[0]][action[1]] = '.'
        self.valid_moves.append(action)

    def checkEdge(self, color, node):
        if color == 'W' and node[1] == self.BOARD_SIZE[1]-1:
            return True
        if color == 'B' and node[0] == self.BOARD_SIZE[0]-1:
            return True
        return False
                
    def testConnections(self, cellToCheck):
        print('connections are', self.cell_connections(cellToCheck))

    def printBoard(self):
        for i in range(self.BOARD_SIZE[0]):
            print('  '*(self.BOARD_SIZE[0]-i-1), end='')
            for j in range(self.BOARD_SIZE[1]):
                print(self.BOARD[i][j], end=' ')
            print('')

    def placeStone(self, cell, color):
        if self.BOARD[cell[0]][cell[1]] != '.':
            print('Invalid Action')
            return False
        self.BOARD[cell[0]][cell[1]] = color
        return True

    def cell_connections(self, cell):
        row = cell[0] 
        col = cell[1]

        positions = []
        
        if col + 1 < self.BOARD_SIZE[1]:
            positions.append([row, col + 1])
        if col - 1 >= 0:
            positions.append([row, col - 1])
        if row + 1 < self.BOARD_SIZE[0]:
            positions.append([row + 1, col])
            if col + 1 < self.BOARD_SIZE[1]:
                positions.append([row + 1, col + 1])
        if row - 1 >= 0:
            positions.append([row - 1, col])
            if col - 1 >= 0:
                positions.append([row - 1, col - 1])
        
        return positions
    
    def check_game_status(self):
        # checking for white
        self.CHECK_BOARD = [[False for _ in range(self.BOARD_SIZE[0])] for _ in range(self.BOARD_SIZE[1])] 
        for i in range(self.BOARD_SIZE[0]):
            if self.BOARD[i][0] == 'W':
                self.CHECK_BOARD[i][0] = True
                self.check_connections(self.cell_connections([i, 0]), 'W')
                if self.done:
                    self.done = False
                    return 'W'
        # checking for black
        self.CHECK_BOARD = [[False for _ in range(self.BOARD_SIZE[0])] for _ in range(self.BOARD_SIZE[1])] 
        for i in range(self.BOARD_SIZE[1]):
            if self.BOARD[0][i] == 'B':
                self.CHECK_BOARD[0][i] = True
                self.check_connections(self.cell_connections([0, i]), 'B')
                if self.done:
                    self.done = False
                    return 'B'
        return '='

    def check_connections(self, connections, color):
        for c in connections:
            if self.BOARD[c[0]][c[1]] == color and not self.CHECK_BOARD[c[0]][c[1]]:
                # print(c[0], c[1], 'visited')
                if self.checkEdge(color, c):
                    self.done = True
                    return
                self.CHECK_BOARD[c[0]][c[1]] = True
                self.check_connections(self.cell_connections([c[0], c[1]]), color)