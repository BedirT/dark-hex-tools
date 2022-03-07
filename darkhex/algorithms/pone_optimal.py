import copy
import math
from itertools import combinations, permutations
from time import time

import numpy as np
from utils.pit import pit

from utils.hex import Hex

C_PLAYER1 = 'x'
C_PLAYER2 = 'o'
EMPTY_CELL = '.'
ILLEGAL = 'i'
TIE = '='

def RES_CHECK(s, h):
    if CHECK and TO_CHECK_STATE == s and TO_CHECK_H == h:
        return True
    return False


class PoneOptimal:
    
    def __init__(self, board_size):
        self.num_rows = board_size[0]
        self.num_cols = board_size[1]
        self.num_cells = self.num_rows * self.num_cols

        self.state_results = [{} for _ in range(self.num_cells + 1)]

        self.player = C_PLAYER2  # manually set
        self.opponent = C_PLAYER1 if self.player == C_PLAYER2 else C_PLAYER2
        self.find_positions()


    def pone_search(self, state: str, h: int) -> bool:
        """
        Recursive algorithm to iterate through sub states and
        determine if the given position is a prob 1 win for player
        or not.

        Args:
            - state:    State to check the legality.
            - h:        Number of hidden stones.
        Returns:
            - True/False  If given state and h is a definite win
        """
        status = self.state_results[h][state]

        if status in [self.player, self.opponent]:
            return status

        if self.turn_info(state, h) != self.player:
            if self.check_state(state, h + 1):
                return self.pone_search(state, h + 1)
        else:
            vm = [i for i, x in enumerate(state) if x == EMPTY_CELL]
            if h == 0:
                for x in vm:
                    n_state = self.update_state(state, x, self.player, h)
                    if n_state in self.state_results[h] and self.pone_search(n_state, h):
                        self.state_results[h][n_state] = self.player
                        return self.player
            elif h > 0:
                for y in vm:
                    n_state_hW = self.update_state(state, y, self.opponent, h - 1)  # hit the hidden stone
                    if n_state_hW not in self.state_results[h - 1]:
                        continue
                    n_state_B = self.update_state(state, y, self.player, h)
                    if (n_state_B in self.state_results[h]
                        and self.pone_search(n_state_hW, h - 1)
                        and self.pone_search(n_state_B, h)):
                        self.state_results[h][n_state_B] = self.player
                        self.state_results[h - 1][n_state_hW] = self.player
                        return self.player
        return False

    def update_state(self, state: str, loc: int, player: str, h: int) -> list:
        """
        Update the given state, make a move on given location by
        the given player, and check if the new state is legal.

        Args:
            - state:    State to check the legality.
            - loc:      Location to put the new stone.
            - player:    The player which will make the move.
            - h:        Number of hidden stones.
        Returns:
            - new_state/[]  New state, if move made to loc by player(player)
                            is valid, empty list (False) otherwise
        """
        new_state = list(copy.deepcopy(state))
        new_state[loc] = player
        new_state = "".join(new_state)
        if self.check_state(new_state, h):
            return new_state
        return ""

    def check_state(self, state: str, h: int) -> str:
        """
        Checks the state and determines if legal. Updates
        state_results accordingly if the given state and h
        is legal.

        Args:
            - state:    State to check the legality.
            - h:        Number of hidden stones.
        Returns:
            - res/False Immediate game status for the given state
                        (Black win - White win - Tie) (B, W, =)
        """
        res = self.is_legal(state, h)
        if res:
            self.state_results[h][state] = res
            return res
        return False

    def turn_info(self, state: str, h: int) -> str:
        """
        Checks which players turn is it given the state and
        the number of hidden stones.

        Args:
            - state:    State to check the legality.
            - h:        Number of hidden stones.
        Returns:
            - C_PLAYER1/C_PLAYER2   Player whose turn it is.
        """
        count_player = state.count(self.player)
        count_opp = state.count(self.opponent) + h

        if self.player == C_PLAYER1 and count_player <= count_opp:
            return C_PLAYER1
        elif count_opp <= count_player:
            return C_PLAYER1
        return C_PLAYER2

    def find_positions(self) -> None:
        """
        Find all the legal positions, examine every position
        in depth for prob 1 wins for players. It fills the dictionary
        'state results'.
        """
        for e in pit(range(self.num_cells + 1), color="red"):  # empty cells
            for h in pit(range(math.ceil(self.num_cells / 2)), color="green"):  # hidden cells
                if e + h > self.num_cells:
                    continue
                states = self.all_states(e + h)
                print(states)
                for s in pit(range(len(states)), color="blue"):
                    state = states[s]
                    try:
                        res = self.state_results[h][state]
                    except:
                        res = self.is_legal(state, h)
                    if res:  # if res is legal
                        self.state_results[h][state] = res
                        if self.pone_search(state, h):
                            self.state_results[h][state] = self.player

    def is_legal(self, state: str, h: int) -> str:
        """
        Check the given state and determine the legality. If
        the state is legal examine the immediate result of the
        state (White/Black(W/B) wins or a tie-(=)).

        Args:
            - state:    State to check the legality.
            - h:        Number of hidden stones.
        Returns:
            - gs/False  Immediate game status for the given state
                        (Black win - White win - Tie) (B, W, =)
        """
        game = Hex(
            board_size=[self.num_rows, self.num_cols],
            board=list(state),
            legality_check=True,
            h=h,
        )
        info_sets = True
        if h > 0:
            # if partial position, check info sets
            info_sets = self.information_sets(state, h)
        # Check if the state has odd or even number of
        # empty cells.
        e = game.board.count(EMPTY_CELL) - h
        if (self.num_cells - e) % 2 == 0:
            # k = 2n
            game.w_early_w = True  # check for early White win set
            gs = game.game_status()
            if gs not in [ILLEGAL, C_PLAYER1] and info_sets:
                return gs
        else:
            # k = 2n + 1
            game.b_early_w = True  # check for early Black win set
            gs = game.game_status()
            if gs not in [ILLEGAL, C_PLAYER2] and info_sets:
                return gs
        return False

    def information_sets(self, state: str, h: int) -> bool:
        """
        Checks if an information exists for the given position.

        Args:
            - state:    State to check the existing information sets.
            - h:        Number of hidden stones on the board.
        Return:
        """
        indexes_empty = [i for i, x in enumerate(state) if x == EMPTY_CELL]
        comb = combinations(indexes_empty, h)
        for c in comb:
            # place the stones on chosen indexes
            p = [x if i not in c else C_PLAYER2 for i, x in enumerate(state)]
            # check if legal
            if self.is_legal(p, 0):
                return True
        return False

    def all_states(self, e: int) -> list:
        """
        Returns all the board states possible given e, number of
        empty cells. Fills rest of the board with corresponding
        Black and White stones, keeping only the ones that are
        possible legal.

        Args:
            - e:    Number of empty cells for the board
                    states to be created.

        Returns:
            - ls:   List of all possible states for e.
        """
        ls = []
        for num_w in range(self.num_cells // 2 + 1):
            num_b = self.num_cells - e - num_w
            if (
                num_w <= num_b
                and num_b <= math.ceil(self.num_cells / 2)
                and not (e + num_b + num_w > self.num_cells)
            ):
                for positions in combinations(range(self.num_cells), num_w + num_b):
                    seq = np.array(["."] * self.num_cells)
                    seq[list(positions[: num_b + 1])] = self.player
                    seq[list(positions[num_b + 1 :])] = self.opponent
                    ls.append("".join(seq))
        return ls
