C_PLAYER1 = 'x'
C_PLAYER2 = 'o'
EMPTY_CELL = '.'
ILLEGAL = 'i'
TIE = '='

class Hex:

    def __init__(self, board_size, board, legality_check=False,
                 b_early_w=False, w_early_w=False, h=0):
        self.num_rows = board_size[0]
        self.num_cols = board_size[1]
        self.num_cells = self.num_rows * self.num_cols

        self.board = board
        self.valid_moves = list(range(self.num_cells))

        self.done = False
        self.legality_check = legality_check
        self.b_early_w = b_early_w
        self.w_early_w = w_early_w
        self.h = h
        self.CHECK = False
        
    def _checkEdge(self, color, node):
        if (color == C_PLAYER2 and self._find_col(node) == self.num_cols-1) or \
           (color == C_PLAYER1 and self._find_row(node) == self.num_rows-1):
            return True
        return False

    def _find_row(self, node):
        return node // self.num_cols

    def _find_col(self, node):
        return node % self.num_cols

    def _cell_connections(self, cell):
        row = self._find_row(cell)
        col = self._find_col(cell)

        positions = []
        if col + 1 < self.num_cols:
            positions.append(self._pos_by_coord(row, col + 1))
        if col - 1 >= 0:
            positions.append(self._pos_by_coord(row, col - 1))
        if row + 1 < self.num_rows:
            positions.append(self._pos_by_coord(row + 1, col))
            if col - 1 >= 0:
                positions.append(self._pos_by_coord(row + 1, col - 1))
        if row - 1 >= 0:
            positions.append(self._pos_by_coord(row - 1, col))
            if col + 1 < self.num_cols:
                positions.append(self._pos_by_coord(row - 1, col + 1))
        return positions
    
    def _pos_by_coord(self, r, c):
        return self.num_cols * r + c

    def game_status(self):
        '''
        Checks the game status by looking at the board and determining the winning player if any, returning
        the winner, or '=' if there is no winner.

        returns:
            format >> C_PLAYER2/C_PLAYER1/'='/'i'

            C_PLAYER2/C_PLAYER1/'=' - winner is white/black or its a tie ('=')
            'i'         - illegal game position
        '''
        # Check for legality
        if self.legality_check:
            if not self.check_legal():
                if self.CHECK:
                    self.CHECK = False
                return ILLEGAL

        # checking for black
        self.CHECK_BOARD = [False for _ in range(self.num_cells)] 
        for i in range(self.num_cols):
            pos = self._pos_by_coord(0, i)
            if self.board[pos] == C_PLAYER1:
                self.CHECK_BOARD[pos] = True
                self._check_connections(self._cell_connections(pos), C_PLAYER1)
                if self.done:
                    self.done = False
                    return C_PLAYER1
        # checking for white
        self.CHECK_BOARD = [False for _ in range(self.num_cells)]
        for i in range(self.num_rows):
            pos = self._pos_by_coord(i, 0)
            if self.board[pos] == C_PLAYER2:
                self.CHECK_BOARD[pos] = True
                self._check_connections(self._cell_connections(pos), C_PLAYER2)
                if self.done:
                    self.done = False
                    return C_PLAYER2
        return TIE 

    def _check_connections(self, connections, color):
        '''
        Checking and following all the given connections for the given color, and changes the done status
        to the winner if finds a connection to the edge of the board.

        args:
            connections - The connections to follow for searching the end edge.
            color       - The color to check the connections for
        '''
        for c in connections:
            if self.board[c] == color and not self.CHECK_BOARD[c]:
                if self._checkEdge(color, c):
                    self.done = True
                    return
                self.CHECK_BOARD[c] = True
                self._check_connections(self._cell_connections(c), color)

    def check_legal(self):
        # number of the stones are illegal
        bNum = self.board.count(C_PLAYER1)
        wNum = self.board.count(C_PLAYER2)
        if (self.h + bNum + wNum > self.num_cells) or \
           (bNum - (wNum + self.h) > 1 or (wNum + self.h) > bNum):
            return False
        
        # white wins with removing a white stone
        if self.w_early_w and self.check_early_win(C_PLAYER2):
            return False
        # black wins with removing a black stone
        if self.b_early_w and self.check_early_win(C_PLAYER1):
            return False

        return True
            
    def check_early_win(self, color):
        for c in range(len(self.board)):
            if self.board[c] in [C_PLAYER1, C_PLAYER2]:
                continue
            temp = self.board[c]
            self.board[c] = EMPTY_CELL; self.legality_check = False
            res = self.game_status()
            self.board[c] = temp; self.legality_check = True
            if res == color:
                return True     
