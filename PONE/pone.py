# Already counted all permutations
# format:
#   X.WX.WW.X

# lets change the game to use these string format instead of arrays

# PONE (Probability One)
# Finding prob one winning states up to given depth (bottom up)
from itertools import combinations, permutations
import math
import copy

from game.hex import Hex
from util.pit import pit

class PONE:
    def __init__(self, board_size):
        self.num_rows = board_size[0]
        self.num_cols = board_size[1]
        self.num_cells = self.num_rows * self.num_cols

        self.color = 'B' # manually set
        self.opp_color = 'B' if self.color == 'W' else 'W'

        self.state_results = {}
        self.prob1_wins = []
        self.find_positions()
        
    def ryan_alg(self, state, h):
        vm = [i for i, x in enumerate(state) if x == '.']
        next_move = True # if there is a next move
        # if white's turn - play white and continue (add a hidden stone)
        if self.turn_info(state, h) != self.color:
            if self.check_state(state, h+1): # white made a move, if not illegal
                h += 1 # white plays
            else:
                next_move = False # There is no next move

        try:
            status = self.state_results[(*state, h)]
        except:
            print("ERROR: Couldn't find the state in state_results", (*state, h))
            print(self.state_results); exit()
                
        if status == self.color:
            return True
        elif status == self.opp_color or not next_move:
            return False 
        else: # status == '='
            if h == 0:
                for x in vm:
                    n_state = self.update_state(state, x, self.color, h) # black moves
                    if (*n_state, h) in self.state_results \
                        and self.ryan_alg(n_state, h):
                        return True
            elif h > 0:
                # if h+1 > self.num_cells//2:
                #     return False
                for y in vm:
                    n_state_hW = self.update_state(state, y, self.opp_color, h-1) # hit the hidden stone
                    n_state_B  = self.update_state(state, y, self.color, h) # black plays
                    # check if black won
                    if  (*n_state_hW, h-1) in self.state_results and \
                        (*n_state_B, h) in self.state_results and \
                        self.ryan_alg(n_state_hW, h-1) and \
                        self.ryan_alg(n_state_B, h):
                        return True
        return False
    
    def update_state(self, state, add, color, h):
        new_state = list(copy.deepcopy(state))
        new_state[add] = color
        if self.check_state(new_state, h):
            return new_state
        return []
    
    def check_state(self, state, h):
        res = self.is_legal(state, h)
        if res:
            self.state_results[(*state, h)] = res
            return res
        return False

    def turn_info(self, state, h):
        '''
        Check which players turn is it
        '''
        count_b = state.count('B')
        count_w = state.count('W') + h
        if count_b <= count_w:
            return 'B'
        else:
            return 'W'

    def find_positions(self):
        for e in pit(range(self.num_cells), color='red'): # empty cells
            for h in pit(range(self.num_cells//2), color='green'): # hidden cells
                # e = 4; h = 0
                states = self.all_states(e, h)
                for s in pit(range(len(states)), color='blue'):
                    state=states[s]
                    if (*state, h) not in self.state_results:
                        res = self.is_legal(state, h)
                    else:
                        res = self.state_results[(*state, h)]
                    if res: 
                        self.state_results[(*state, h)] = res
                        # if CHECK == (*state, h):
                        #     global ACTIVATE_CHECK
                        #     ACTIVATE_CHECK = True
                        if self.ryan_alg(state, h):
                            self.state_results[(*state, h)] = self.color
                            self.prob1_wins.append((state, h))
                            # if ACTIVATE_CHECK:
                            #     ACTIVATE_CHECK = False

    def is_legal(self, state, h):
        # Check if the given state is legal
        # if so is it B winning or W winning
        # play a game
        game = Hex(BOARD_SIZE=[self.num_rows, self.num_cols], 
                                BOARD=list(state), legality_check=True,
                                h = h)
        info_sets = True
        if h > 0:
            # if partial position, check info sets
            info_sets = self.information_sets(state, h)
        # Check if the state has odd or even number of
        # empty cells.
        # if CHECK == (*state, h):
        #     print(info_sets)
        e = game.BOARD.count('.') - h
        if (self.num_cells - e) % 2 == 0:
            # k = 2n
            # if (*state, h) == CHECK:
            #     game.CHECK = True
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

    def information_sets(self, pos, h):
        '''
        Do we not need all info-sets?
        According to algo only finding that there is one 
        exists is enough?
        '''
        indexes_empty = [i for i, x in enumerate(pos) if x == '.']
        comb = combinations(indexes_empty, h)
        for c in comb:
            # place the stones on chosen indexes
            p = [x if i not in c else 'W' for i, x in enumerate(pos)]
            # check if legal
            if self.is_legal(p, 0):
                return True
        return False

    def all_states(self, e, h):
        '''
        Returns all the board states possible
        '''
        ls = []
        for num_w in range(self.num_cells//2 + 1):
            num_b = (self.num_cells - e - h - num_w)
            seq = '.' * (e + h) + self.opp_color * num_w + \
                  self.color * num_b
            if num_w <= num_b and num_b <= math.ceil(self.num_cells/2):
                ls.extend(list(set(permutations(seq))))
        return ls