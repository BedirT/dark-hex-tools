# Already counted all permutations
# format:
#   X.WX.WW.X

# lets change the game to use these string format instead of arrays

# PONE (Probability One)
# Finding prob one winning states up to given depth (bottom up)
from itertools import combinations, permutations
from game.hex import Hex
import copy 
import pickle

from tqdm import tqdm

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
        game = Hex(BOARD_SIZE=[self.num_rows, self.num_cols], BOARD=state)
        vm = game.valid_moves

        try:
            status = self.state_results[(*state, e, h)]
        except:
            print((*state, e, h))
            print(self.state_results)
            exit()
        print(e, h, state)
        if status == self.color:
            print('here')
            return True
        elif status == self.opp_color:
            print('here2')
            return False 
        else: # status == '='
            print('here3')
            if h == 0:
                print('here4')
                for x in vm:
                    print('here5')
                    n_state = self.update_state(state, x, self.color)
                    if (*n_state, e, h) in self.state_results \
                        and self.ryan_alg(n_state, e, h+1):
                        return True
            elif h > 0:
                print('here6')
                for y in vm:
                    print('here7')
                    n_state_W = self.update_state(state, y, self.opp_color)
                    n_state_B = self.update_state(state, y, self.color)
                    if n_state_W and n_state_B and \
                       self.ryan_alg(n_state_W, e, h-1) and \
                       self.ryan_alg(n_state_B, e, h+1):
                        return True
        return False
    
    def update_state(self, state, add, color):
        new_state = list(copy.deepcopy(state))
        new_state[add] = color
        return new_state

    def find_positions(self):
        for e in range(self.num_cells): # empty cells
            for h in range(self.num_cells//2): # hidden cells
                states = self.all_states(e, h)
                for state in tqdm(states):
                    res = self.is_legal(state, e, h)
                    if res:
                        self.state_results[(*state, e, h)] = res
                        print((*state, e, h))
                        if self.ryan_alg(state, e, h):
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
            if game.game_status() not in 'Bi' and info_sets:
                return game.game_status()
        else:
            # k = 2n + 1
            game.b_early_w = True # check for early Black win set
            if game.game_status() not in 'Wi' and info_sets:
                return game.game_status()

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
            if tuple(p) in self.state_results:
                # key exists, therefore legal
                return True
        return False

    def all_states(self, e, h):
        '''
        Returns all the board states possible
        '''
        ls = []
        for num_w in range(self.num_cells//2):
            seq = '.' * (e + h) + self.opp_color * num_w + \
                  self.color * (self.num_cells - e - h - num_w)
            ls.extend(list(set(permutations(seq))))
        return ls

p = PONE([2,2])
print(len(p.prob1_wins))

with open('prob1_2x2.pkl', 'wb') as f:
    pickle.dump(p.prob1_wins, f)