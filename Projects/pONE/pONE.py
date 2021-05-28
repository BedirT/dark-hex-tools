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

from Projects.base.game.hex import Hex, customBoard_print
from Projects.base.util.pit import pit
from Projects.base.util.colors import pieces

CHECK = True
TO_CHECK_STATE =('W','.','B',
                   'W','.','.',
                     'B','.','.')
TO_CHECK_H = 0
TO_CHECK_E = 5

def RES_CHECK(s, h, e):
    if CHECK and TO_CHECK_STATE == s and TO_CHECK_H == h \
        and TO_CHECK_E == e:
        return True
    return False

class pONE:
    def __init__(self, board_size, visible_player):
        '''
        player_to_run - 1: Run for the first player
                      - 2: Run for the second player
        '''
        self.num_rows = board_size[0]
        self.num_cols = board_size[1]
        self.num_cells = self.num_rows * self.num_cols

        self.color1 = pieces.C_PLAYER1
        self.color2 = pieces.C_PLAYER2
        self.neutral = pieces.NEUTRAL

        self.vis_p = visible_player # The hidden player
        self.hid_p = self.color1 if self.vis_p == self.color2 else self.color2
        
        self.state_results = [[{} for _ in range(self.num_cells//2+1)] for _ in range(self.num_cells+1)]
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
            status = self.state_results[e][h][state][0]
        except:
            print("ERROR: Couldn't find the state in state_results[{}][{}]:\n\t{}"\
                  .format(e, h, state)); exit()
        if status in [self.color1, self.color2]:
            return status
        else: # status == '='
            if self.turn_info(state, h) != self.vis_p:
                if self.check_state(state, e-1, h+1): # hidden player makes a move, if not illegal
                    res = self.pONE_search(state, e-1, h+1)
                    if res in [self.color1, self.color2]:
                        self.distance += self.find_distance(state, e-1, h+1) + 1
                        return res
                    return False
            else:
                vm = [i for i, x in enumerate(state) if x == self.neutral]
                for v in vm:
                    if h == 0:
                        n_state_b = self.update_state(state, v, self.vis_p, e-1, h) # black moves
                        if n_state_b == self.vis_p:
                            self.distance += self.find_distance(state, e-1, h) + 1
                            return self.vis_p
                    elif h > 0:
                        n_state_w = self.update_state(state, v, self.hid_p, e, h-1) # hit the hidden stone
                        n_state_b = self.update_state(state, v, self.vis_p, e-1, h) # black plays
                        if n_state_b == self.vis_p and n_state_w == self.vis_p:
                            self.distance += min(self.find_distance(state, e, h-1),\
                                                 self.find_distance(state, e-1, h)) + 1
                            return self.vis_p
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
        if h >= len(self.state_results[0]) or e >= len(self.state_results):
            return False
        if state in self.state_results[e][h]:
            return self.state_results[e][h][state][0]
        return False

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
        count_1 = state.count(self.color1)
        count_2 = state.count(self.color2)
        if self.hid_p == self.color1:
            count_1 += h
        else:
            count_2 += h
        if count_1 <= count_2:
            return self.color1
        else:
            return self.color2

    def find_distance(self, state: tuple, e: int, h: int) -> int:
        return int(self.state_results[e][h][state][2:])

    def find_positions(self) -> None:
        '''
        Find all the legal positions, examine every position
        in depth for prob 1 wins for players. It fills the dictionary
        'state results'.
        '''
        tot = 0; tot1 = 0
        time1 = time()
        print('Finding all legal states...')
        for e in pit(range(self.num_cells+1), color='purple'): # empty cells
            for h in pit(range(self.num_cells//2+1), color='grey'): # hidden cells
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
        for e in pit(range(self.num_cells+1), color='red'): # empty cells
            for h in pit(range(self.num_cells//2+1), color='green'): # hidden cells
                if e+h >= self.num_cells:
                    continue
                for state in pit(self.state_results[e][h], color='blue'):
                    self.distance = 0
                    res = self.pONE_search(state, e, h)
                    if res:
                        if self.is_terminal(state):
                            self.state_results[e][h][state] = res + 't' + str(self.distance)
                        else:    
                            self.state_results[e][h][state] = res + 'x' + str(self.distance)
        time2_end = time()

        # reporting the timing for part1 and 2
        tot = time2_end - time1; tot1 = time1_end - time1
        print('Part1\t\t\tPart2\n{}'.format('='*45))
        print(tot1/tot, '\t' ,(tot - tot1)/tot)
        print(tot1, '\t' ,tot - tot1)
        print('Total time:', tot)
        
    def is_terminal(self, state):
        game = Hex(BOARD_SIZE=[self.num_rows, self.num_cols], 
                                BOARD=list(state))
        res = game.game_status()
        if res in [self.color1, self.color2]:
            return True
        return False

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
                                h = h, h_player=self.hid_p)
        info_sets = True
        if h > 0:
            # if partial position, check info sets
            info_sets = self.information_sets(state, e, h)
        # Check if the state has odd or even number of
        # empty cells.
        if (self.num_cells - e) % 2 == 0:
            # k = 2n
            game.early_w_p2  = True # check for early White win set
            gs = game.game_status()
            if gs != 'i' and info_sets:
                return gs
        else:
            # k = 2n + 1
            game.early_w_p1 = True # check for early Black win set
            gs = game.game_status()
            if gs != 'i' and info_sets:
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
        indexes_empty = [i for i, x in enumerate(state) if x == self.neutral]
        comb = combinations(indexes_empty, h)
        for c in comb:
            # place the stones on chosen indexes
            p = [x if i not in c else self.hid_p for i, x in enumerate(state)]
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
        for num_2nd in range(self.num_cells//2 + 1):
            num_1st = (self.num_cells - e - num_2nd) 

            if (self.color1 == self.vis_p and \
                (num_2nd <= num_1st and num_1st <= math.ceil(self.num_cells/2) and \
                 not (e + num_1st + num_2nd > self.num_cells))
               ) or ( self.color2 == self.vis_p and \
                (num_1st <= math.ceil(self.num_cells/2) and \
                 not (e + num_1st + num_2nd > self.num_cells) and \
                 num_1st >= 0
               )):
                for pos_b in combinations(range(self.num_cells), num_1st):
                    for pos_w in combinations(set(range(self.num_cells))-set(pos_b), num_2nd):
                        seq = np.array([self.neutral] * self.num_cells)
                        seq[list(pos_b)] = self.color1
                        seq[list(pos_w)] = self.color2
                        ls.append(tuple(seq))
        return ls