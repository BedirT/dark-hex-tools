# Already counted all permutations
# format:
#   X.WX.WW.X

# lets change the game to use these string format instead of arrays

# PONE (Probability One)
# Finding prob one winning states up to given depth (bottom up)
import numpy as np
from itertools import combinations_with_replacement, product
from game.darkHex import DarkHex
from game.hex import Hex
import copy 

from tqdm import tqdm

class PONE:
    def __init__(self, board_size, color):
        self.num_rows = board_size[0]
        self.num_cols = board_size[1]
        self.num_elements = self.num_rows * self.num_cols

        self.results = {}
        self.color = color
        self.opp_color = 'B' if color == 'W' else 'W'

        ls = self.all_permutations()
        self.examine_positions(ls)

        print(self.ryan_alg(['.', '.', '.', 
                                '.', 'B', '.', 
                                    'B', '.', '.'], 2))
        
    def ryan_alg(self, state, h):
        game = Hex(BOARD_SIZE=[self.num_rows, self.num_cols], BOARD=state)
        vm = game.valid_moves

        w = self.results[tuple(state)]
        print(state, w, h)
        if w == self.color:
            print('in')
            return True
        elif not w == self.opp_color:
            print('in 2')
            if h == 0:
                print('in 3')
                for x in vm:
                    n_state = self.update_state(state, x, self.color)
                    if n_state and self.ryan_alg(n_state, h+1):
                        return True
            elif h > 0:
                print('in 4')
                for y in vm:
                    print('in 5')
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
        if self.results[tuple(new_state)] == 'i':
            return False
        return new_state

    def examine_positions(self, ls_positions):
        '''
        For each position decides if;
            - White win
            - Black win
            - Illegal
        Returns ?
        '''
        ct_w = 0; ct_i = 0; ct_b = 0; ct_non = 0
        for positions in ls_positions:
            for pos in tqdm(positions):
                game = Hex(BOARD_SIZE=[self.num_rows, self.num_cols], BOARD=list(pos), legality_check=True)
                res = game.game_status()
                self.results[pos] = res
                if res == 'B': ct_b += 1
                elif res == 'W': ct_w += 1
                elif res == '=': ct_non += 1
                else: ct_i += 1
        print('W: {} / B: {} / Non-Terminal: {} / Illegal: {}'.format(
            ct_w, ct_b, ct_non, ct_i
        ))

    def all_permutations(self):
        '''
        Returns all the board states possible
        '''
        ls_w_num_h = [[] for _ in range(self.num_elements + 1)] 
        perms = [p for p in product('BW.', repeat=self.num_elements)]
        for perm in perms:
            num_of_empty = perm.count('.')
            ls_w_num_h[num_of_empty].append(perm)
        return ls_w_num_h

p = PONE([3,3], 'B')