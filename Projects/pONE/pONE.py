# pONE (Probability One)
#
# Finds all probability one wins for the given player
# for the game Hex. 
# Traverses every legal game state recursively, and marks
# the win states with probability one.
#
# DP Version - Eliminates the need of excessive recursion

from itertools import combinations
import math
import copy
from time import time
import numpy as np

from Projects.base.game.hex import Hex
from Projects.base.util.pit import pit
from Projects.base.util.colors import pieces

CHECK = True
TO_CHECK_STATE = ('B', 'B', 'W', 'W')# ('.', '.', '.', '.', '.', '.', 'B', '.', '.') # ('.', 'B', '.', '.')
TO_CHECK_H = 0

def RES_CHECK(s, h):
    if CHECK and TO_CHECK_STATE == s and TO_CHECK_H == h:
        return True
    return False

class pONE:
    # Colors for the players
    C_PLAYER1 = pieces.C_PLAYER1
    C_PLAYER2 = pieces.C_PLAYER2

    def __init__(self, board_size, player_to_run=1):
        self.num_rows = board_size[0]
        self.num_cols = board_size[1]
        self.num_cells = self.num_rows * self.num_cols

        self.color = self.C_PLAYER1 # manually set
        self.opp_color = self.C_PLAYER1 if self.color == self.C_PLAYER2 else self.C_PLAYER2

        self.state_results = [[{} for _ in range(self.num_cells//2+1)] for _ in range(self.num_cells)]
        self.prob1_wins = []
        self.find_positions()
    
    def pONE_search(self, state: tuple, e: int, h: int) -> bool:
        '''
        Recursive algorithm to iterate through sub states and
        determine if the given position is a prob 1 win for player
        or not.

        Args:
            - state:    State to check the legality.
            - h:        Number of hidden stones.
        Returns:
            - True/False  If given state and h is a definite win
        '''
        try:
            status = self.state_results[e][h][state]
        except:
            print("ERROR: Couldn't find the state in state_results[{}][{}]:\n\t{}"\
                  .format(e, h, state)); exit()
        if status == self.color:
            return True
        elif status == self.opp_color:
            return False 
        else: # status == '='
            if self.turn_info(state, h) != self.color:
                if self.check_state(state, e-1, h+1): # white made a move, if not illegal
                    # h += 1 # white plays
                    if self.pONE_search(state, e-1, h+1):
                        return True
                return False # There is no next move
            else:
                vm = [i for i, x in enumerate(state) if x == '.']
                for v in vm:
                    if h == 0:
                        n_state_b = self.update_state(state, v, self.color, e-1, h) # black moves
                        if n_state_b == self.color:
                            return True
                    elif h > 0:
                        n_state_w = self.update_state(state, v, self.opp_color, e, h-1) # hit the hidden stone
                        n_state_b  = self.update_state(state, v, self.color, e-1, h) # black plays
                        if n_state_b == self.color and n_state_w == self.color:
                            return True
        return False

    def update_state(self, state: tuple, loc: int, color: str, e: int, h: int) -> list:
        '''
        Update the given state, make a move on given location by
        the given player, and check if the new state is legal.

        Args:
            - state:    State to check the legality.
            - loc:      Location to put the new stone.
            - color:    The player which will make the move.
            - h:        Number of hidden stones.
        Returns:
            - new_state/[]  New state, if move made to loc by player(color)
                            is valid, empty list (False) otherwise
        '''
        new_state = list(copy.deepcopy(state))
        new_state[loc] = color
        new_state = tuple(new_state)
        return self.check_state(new_state, e, h)
    
    def check_state(self, state: tuple, e: int, h: int) -> str:
        '''
        Checks the state and determines if legal. Updates 
        state_results accordingly if the given state and h
        is legal.

        Args:
            - state:    State to check the legality.
            - h:        Number of hidden stones.
        Returns:
            - res/False Immediate game status for the given state
                        (Black win - White win - Tie) (B, W, =)
        '''
        if state in self.state_results[e][h]:
            return self.state_results[e][h][state]
        return ()

    def turn_info(self, state: tuple, h: int) -> str:
        '''
        Checks which players turn is it given the state and
        the number of hidden stones.
        
        Args:
            - state:    State to check the legality.
            - h:        Number of hidden stones.
        Returns:
            - C_PLAYER1/C_PLAYER2   Player whose turn it is.
        '''
        count_b = state.count(self.C_PLAYER1)
        count_w = state.count(self.C_PLAYER2) + h
        if count_b <= count_w:
            return self.C_PLAYER1
        else:
            return self.C_PLAYER2

    def find_positions(self) -> None:
        '''
        Find all the legal positions, examine every position
        in depth for prob 1 wins for players. It fills the dictionary
        'state results'.
        '''
        tot = 0; tot1 = 0
        time1 = time()
        print('Finding all legal states...')
        for e in pit(range(self.num_cells), color='purple'): # empty cells
            for h in pit(range(self.num_cells//2), color='grey'): # hidden cells
                if e+h >= self.num_cells:
                    continue
                states = self.all_states(e + h)
                for s in pit(range(len(states)), color='white'):
                    state = states[s]
                    res = self.is_legal(state, e, h)
                    if res: # if res is legal
                        self.state_results[e][h][state] = res
        time1_end = time()

        print('Finding winning moves...')
        for e in pit(range(self.num_cells), color='red'): # empty cells
            for h in pit(range(self.num_cells//2), color='green'): # hidden cells
                if e+h >= self.num_cells:
                    continue
                for state in pit(self.state_results[e][h], color='blue'):
                    if self.pONE_search(state, e, h):
                        self.state_results[e][h][state] = self.color
        time2_end = time()

        # reporting the timing for part1 and 2
        tot = time2_end - time1; tot1 = time1_end - time1
        print('Part1\t\t\tPart2\n{}'.format('='*45))
        print(tot1/tot, '\t' ,(tot - tot1)/tot)
        print(tot1, '\t' ,tot - tot1)
        print('Total time:', tot)

    def is_legal(self, state: tuple, e:int, h: int) -> str:
        '''
        Check the given state and determine the legality. If 
        the state is legal examine the immediate result of the
        state (White/Black(W/B) wins or a tie-(=)).

        Args:
            - state:    State to check the legality.
            - h:        Number of hidden stones.
        Returns:
            - gs/False  Immediate game status for the given state
                        (Black win - White win - Tie) (B, W, =)
        '''
        game = Hex(BOARD_SIZE=[self.num_rows, self.num_cols], 
                                BOARD=list(state), legality_check=True,
                                h = h)
        info_sets = True
        if h > 0:
            # if partial position, check info sets
            info_sets = self.information_sets(state, e, h)
        # Check if the state has odd or even number of
        # empty cells.
        if (self.num_cells - e) % 2 == 0:
            # k = 2n
            game.w_early_w = True # check for early White win set
            gs = game.game_status()
            if gs not in 'Bi' and info_sets:
                return gs
        else:
            # k = 2n + 1
            gs = game.game_status()
            game.b_early_w = True # check for early Black win set
            if gs not in 'Wi' and info_sets:
                return gs
        return False

    def information_sets(self, state: tuple, e:int, h: int) -> bool:
        '''
        Checks if an information exists for the given position.

        Args:
            - state:    State to check the existing information sets.
            - h:        Number of hidden stones on the board.
        Return:
        '''
        indexes_empty = [i for i, x in enumerate(state) if x == '.']
        comb = combinations(indexes_empty, h)
        for c in comb:
            # place the stones on chosen indexes
            p = [x if i not in c else self.C_PLAYER2 for i, x in enumerate(state)]
            # check if legal
            if self.is_legal(p, e, 0):
                return True
        return False

    def all_states(self, e: int) -> list:
        '''
        Returns all the board states possible given e, number of
        empty cells. Fills rest of the board with corresponding
        Black and White stones, keeping only the ones that are
        possible legal.

        Args: 
            - e:    Number of empty cells for the board
                    states to be created.
        
        Returns:
            - ls:   List of all possible states for e.
        '''
        ls = []
        for num_w in range(self.num_cells//2 + 1):
            num_b = (self.num_cells - e - num_w) 
            if num_w <= num_b and num_b <= math.ceil(self.num_cells/2) and \
                not (e + num_b + num_w > self.num_cells):
                for pos_b in combinations(range(self.num_cells), num_b):
                    for pos_w in combinations(set(range(self.num_cells))-set(pos_b), num_w):
                        seq = np.array(['.'] * self.num_cells)
                        seq[list(pos_b)] = self.color
                        seq[list(pos_w)] = self.opp_color
                        ls.append(tuple(seq))
        return ls