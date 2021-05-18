# PONE old version
# WARNING! - This algorithm is faulty
#            included in the document only
#            for archive reasons. Please do
#            not use it. For the correct version
#            use "PONE/pone.py".

from itertools import combinations, permutations
import math

from game.hex import Hex
import copy 
import pickle

from util.pit import pit

CHECK = ('.', '.', '.','.', 'B', '.','.', '.','.', 8, 0) # supposed to be 'B'
CHECK_CALL_STACK = []
ACTIVATE_CHECK = False

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
        
    def ryan_alg(self, state, e, h):
        vm = [i for i, x in enumerate(state) if x == '.']
        # if (*state, e, h) == CHECK:
        #     print('VM`s', vm)
        try:
            status = self.state_results[(*state, e, h)]
        except:
            print("ERROR: Couldn't find the state in state_results", (*state, e, h))
            print(self.state_results); exit()
        if ACTIVATE_CHECK:
            CHECK_CALL_STACK.append((*state, e, h))
        if status == self.color:
            return True
        elif status == self.opp_color:
            return False 
        else: # status == '='
            if h == 0:
                for x in vm:
                    n_state = self.update_state(state, x, self.color, e-2, h+1)
                    if (*n_state, e-2, h+1) in self.state_results \
                        and self.ryan_alg(n_state, e-2, h+1):
                        return True
            elif h > 0:
                # if h+1 > self.num_cells//2:
                #     return False
                for y in vm:
                    n_state_W = self.update_state(state, y, self.opp_color, e, h-1)
                    n_state_B = self.update_state(state, y, self.color, e-2, h+1)
                    if (*n_state_W, e, h-1) in self.state_results and \
                        (*n_state_B, e-2, h+1) in self.state_results and \
                        self.ryan_alg(n_state_W, e, h-1) and \
                        self.ryan_alg(n_state_B, e-2, h+1):
                        return True
        return False
    
    def update_state(self, state, add, color, e, h):
        new_state = list(copy.deepcopy(state))
        new_state[add] = color
        res = self.is_legal(new_state, e, h)
        if res:
            # if ACTIVATE_CHECK:
                # print('1', (*new_state, e, h))
            self.state_results[(*new_state, e, h)] = res
            return new_state
        return []

    def find_positions(self):
        for e in pit(range(self.num_cells), color='red'): # empty cells
            for h in pit(range(self.num_cells//2), color='green'): # hidden cells
                # e = 4; h = 0
                states = self.all_states(e, h)
                for s in pit(range(len(states)), color='blue'):
                    state=states[s]
                    if (*state, e, h) not in self.state_results:
                        res = self.is_legal(state, e, h)
                    else:
                        res = self.state_results[(*state, e, h)]
                    if res:
                        self.state_results[(*state, e, h)] = res
                        if CHECK == (*state, e, h):
                            global ACTIVATE_CHECK
                            ACTIVATE_CHECK = True
                        if self.ryan_alg(state, e, h):
                            self.state_results[(*state, e, h)] = self.color
                            self.prob1_wins.append((state, e, h))
                            if ACTIVATE_CHECK:
                                ACTIVATE_CHECK = False
                        
    def is_legal(self, state, e, h):
        # Check if the given state is legal
        # if so is it B winning or W winning
        # play a game
        game = Hex(BOARD_SIZE=[self.num_rows, self.num_cols], 
                                BOARD=list(state), legality_check=True,
                                h = h, e = e)
        info_sets = True
        if h > 0:
            # if partial position, check info sets
            info_sets = self.information_sets(state, e, h)
        # Check if the state has odd or even number of
        # empty cells.
        if (self.num_cells - e) % 2 == 0:
            # k = 2n
            # if (*state, e, h) == CHECK:
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

    def information_sets(self, pos, e, h):
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
            if self.is_legal(p, e, 0):
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

p = PONE([2,2])
chcc = [(x, p.state_results[x]) for x in p.state_results if p.state_results[x] != '=']
print(len(chcc))
print(len(p.prob1_wins))

print(p.is_legal(('.','B','B','.'), 1, 1))

# print(chcc)

# for i in p.state_results:
    # print(i, p.state_results[i])

print(len(CHECK_CALL_STACK))
for i in CHECK_CALL_STACK[-1::-1]:
    print(i)

with open('prob1_2x2.pkl', 'wb') as f:
    pickle.dump(p.prob1_wins, f)

with open('prob1_state_res.pkl', 'wb') as f:
    pickle.dump(chcc, f)