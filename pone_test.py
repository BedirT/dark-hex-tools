# Already counted all permutations
# format:
#   X.WX.WW.X

# lets change the game to use these string format instead of arrays

# PONE (Probability One)
# Finding prob one winning states up to given depth (bottom up)
import numpy as np
from itertools import combinations, combinations_with_replacement, permutations, product
from game.darkHex import DarkHex
from game.hex import Hex
import copy 

from tqdm import tqdm

class PONE:
    def __init__(self, board_size, color):
        self.num_rows = board_size[0]
        self.num_cols = board_size[1]
        self.num_cells = self.num_rows * self.num_cols

        self.color = color
        self.opp_color = 'B' if color == 'W' else 'W'

        self.permutations = self.all_permutations()

        self.positions = {}
        self.partial_positions = [{} for _ in range(self.num_cells)]
        
        self.find_positions()
        self.find_partial_positions()

        print(self.ryan_alg(['.', '.', '.', 
                                '.', 'B', '.', 
                                    'B', '.', '.'], 2))
        
    def ryan_alg(self, state, h):
        game = Hex(BOARD_SIZE=[self.num_rows, self.num_cols], BOARD=state)
        vm = game.valid_moves

        w = self.partial_positions[h][tuple(state)]
        # print(state, w, h)
        if w == self.color:
            return True
        elif not w == self.opp_color:
            if h == 0:
                for x in vm:
                    n_state = self.update_state(state, x, self.color)
                    if n_state and self.ryan_alg(n_state, h+1):
                        return True
            elif h > 0:
                for y in vm:
                    n_state_W = self.update_state(state, y, self.opp_color)
                    n_state_B = self.update_state(state, y, self.color)
                    if n_state_W and n_state_B and \
                       self.ryan_alg(n_state_W, h-1) and \
                       self.ryan_alg(n_state_B, h+1):
                        return True
        return False
    
    def update_state(self, state, add, color):
        new_state = copy.deepcopy(state)
        new_state[add] = color
        if self.positions[tuple(new_state)] == 'i':
            return False
        return new_state

    def find_positions(self):
        '''
        For each position decides if;
            - White win
            - Black win
            - Illegal
        Returns ?
        '''
        for e, positions in enumerate(self.permutations):
            for pos in tqdm(positions):
                res = self.check_legal_pos(pos, e)
                if (self.num_cells - e) % 2 == 0:
                    if res not in 'Bi':
                        self.positions[pos] = res
                else:
                    if res not in 'Wi':
                        self.positions[pos] = res

    def find_partial_positions(self):
        # # create new positions
        # for h in range(self.num_cells//2):
        #     # max number of hidden cells will be num_cells//2
        for pos in tqdm(self.positions):
            e = pos.count('.')
            indexes_w = [i for i, x in enumerate(pos) if x == 'W']
            for h in range(self.num_cells//2):
                # get all possible indexes for h (white to remove)
                # iterate through all
                to_rem = combinations(indexes_w, h)
                for tr in to_rem:
                    p = [x if i not in tr else '.' for i, x in enumerate(pos)]
                    game = Hex(BOARD_SIZE=[self.num_rows, self.num_cols], 
                                BOARD=p, legality_check=True,
                                partial_pos=True)
                    res = game.game_status()
                    info = self.information_sets(p, h)
                    if (self.num_cells - e) % 2 == 0:
                        # k = 2n
                        if res not in 'Bi' and not info:
                            self.partial_positions[h][p] = res
                    else:
                        # k = 2n + 1
                        if res not in 'Wi' and not info:
                            self.partial_positions[h][p] = res

    def information_sets(self, pos, h):
        '''
        Do we not need all info-sets?
        According to algo only finding that there is one 
        exists is enough?
        '''
        info_set = []
        indexes_empty = [i for i, x in enumerate(pos) if x == '.']
        comb = combinations(indexes_empty, h)
        for c in comb:
            # place the stones on chosen indexes
            p = [x if i not in c else 'W' for i, x in enumerate(pos)]
            # check if legal
            res = self.check_legal_pos(p, h)
            if (self.num_cells - h) % 2 == 0:
                if res not in 'Bi':
                    return True
                    # info_set.append(p)
            else:
                if res not in 'Wi':
                    return True
                    info_set.append(p)
        return False

    def check_legal_pos(self, pos, h):
        if (self.num_cells - h) % 2 == 0:
            # k = 2n
            game = Hex(BOARD_SIZE=[self.num_rows, self.num_cols], 
                       BOARD=list(pos), legality_check=True,
                       b_early_w=False, w_early_w=True)
            res = game.game_status()
            return res
        else:
            # k = 2n + 1
            game = Hex(BOARD_SIZE=[self.num_rows, self.num_cols], 
                       BOARD=list(pos), legality_check=True,
                       b_early_w=True, w_early_w=False)
            res = game.game_status()
            return res

    def all_permutations(self):
        '''
        Returns all the board states possible
        '''
        ls_w_num_h = [[] for _ in range(self.num_cells + 1)] 
        perms = [p for p in product('BW.', repeat=self.num_cells)]
        for perm in perms:
            num_of_empty = perm.count('.')
            ls_w_num_h[num_of_empty].append(perm)
        return ls_w_num_h

# p = PONE([3,3], 'B')