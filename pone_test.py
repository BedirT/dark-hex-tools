# Already counted all permutations
# format:
#   X.WX.WW.X

# lets change the game to use these string format instead of arrays

# PONE (Probability One)
# Finding prob one winning states up to given depth (bottom up)
from itertools import combinations, permutations
import math

from tqdm.auto import trange
from game.hex import Hex
import copy 
import pickle

from tqdm import tqdm

CHECK = ('B', '.', '.', '.', 2, 1) # supposed to be 'B'
CHECK_CALL_STACK = []
ACTIVATE_CHECK = False

def pit(it, *pargs, **nargs):
    import enlighten
    global __pit_man__
    try:
        __pit_man__
    except NameError:
        __pit_man__ = enlighten.get_manager()
    man = __pit_man__
    try:
        it_len = len(it)
    except:
        it_len = None
    try:
        ctr = None
        for i, e in enumerate(it):
            if i == 0:
                ctr = man.counter(*pargs, **{**dict(leave = False, total = it_len), **nargs})
            yield e
            ctr.update()
    finally:
        if ctr is not None:
            ctr.close()

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
        if (*state, e, h) == CHECK:
            print('VM`s', vm)
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
                    n_state = self.update_state(state, x, self.color, e-1, h+1)
                    if ACTIVATE_CHECK and n_state:
                        print(n_state)
                    if (*n_state, e-1, h+1) in self.state_results \
                        and self.ryan_alg(n_state, e-1, h+1):
                        return True
            elif h > 0:
                # if h+1 > self.num_cells//2:
                #     return False
                for y in vm:    
                    n_state_W = self.update_state(state, y, self.opp_color, e, h-1)
                    n_state_B = self.update_state(state, y, self.color, e-1, h+1)
                    if (*n_state_W, e, h-1) in self.state_results and \
                        (*n_state_B, e-1, h+1) in self.state_results and \
                        self.ryan_alg(n_state_W, e, h-1) and \
                        self.ryan_alg(n_state_B, e-1, h+1):
                        return True
        return False
    
    def update_state(self, state, add, color, e, h):
        new_state = list(copy.deepcopy(state))
        new_state[add] = color
        res = self.is_legal(new_state, e, h)
        if res:
            self.state_results[(*state, e, h)] = res
            return new_state
        return []

    def find_positions(self):
        for e in pit(range(self.num_cells), color='red'): # empty cells
            for h in pit(range(self.num_cells//2), color='green'): # hidden cells
                states = self.all_states(e, h)
                for s in pit(range(len(states)), color='blue'):
                    state=states[s]
                    if (*state, e, h) not in self.state_results:
                        res = self.is_legal(state, e, h)
                    else:
                        res = self.state_results[(*state, e, h)]
                    if res:
                        if (*state, e, h) == CHECK:
                            print('in-activate')
                            global ACTIVATE_CHECK
                            ACTIVATE_CHECK = True
                        self.state_results[(*state, e, h)] = res
                        
                        if self.ryan_alg(state, e, h):
                            self.state_results[(*state, e, h)] = self.color
                            self.prob1_wins.append((state, e, h))
                        

    def is_legal(self, state, e, h):
        # Check if the given state is legal
        # if so is it B winning or W winning
        # play a game
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
            p = [x if i not in c else 'W' for i, x in enumerate(pos)] + [e, 0]
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
# print(len(chcc))
# print(len(p.prob1_wins))

# print(len(CHECK_CALL_STACK))
# for i in CHECK_CALL_STACK[-1::-1]:
#     print(i)

print(p.is_legal(('.', '.', '.', '.'), 4, 1))

with open('prob1_2x2.pkl', 'wb') as f:
    pickle.dump(p.prob1_wins, f)

with open('prob1_state_res.pkl', 'wb') as f:
    pickle.dump(chcc, f)

