# PONE (Probability One)
#
# Finds all probability one wins for the given player
# for the game Hex.
# Traverses every legal game state recursively, and marks
# the win states with probability one.

import copy
import math
from itertools import combinations, permutations
from time import time

import numpy as np
from util.pit import pit


def RES_CHECK(s, h):
    if CHECK and TO_CHECK_STATE == s and TO_CHECK_H == h:
        return True
    return False


class PONE:
    def __init__(self, board_size):
        self.num_rows = board_size[0]
        self.num_cols = board_size[1]
        self.num_cells = self.num_rows * self.num_cols

        self.color = C_PLAYER1  # manually set
        self.opp_color = C_PLAYER1 if self.color == C_PLAYER2 else C_PLAYER2

        self.state_results = [{} for _ in range(self.num_cells)]
        self.prob1_wins = []
        self.find_positions()

    def pone_search(self, state: tuple, h: int) -> bool:
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
        try:
            status = self.state_results[h][state]
        except:
            print(
                "ERROR: Couldn't find the state in state_results[{}] |\n{}".format(
                    h, state
                )
            )
            exit()

        if status == self.color:
            return True
        elif status == self.opp_color:
            return False
        else:  # status == '='
            # if white's turn - play white and continue (add a hidden stone)
            if self.turn_info(state, h) != self.color:
                if self.check_state(state, h + 1):  # white made a move, if not illegal
                    # h += 1 # white plays
                    if self.pone_search(state, h + 1):
                        return True
                return False  # There is no next move
            else:
                vm = [i for i, x in enumerate(state) if x == "."]
                if h == 0:
                    for x in vm:
                        n_state = self.update_state(
                            state, x, self.color, h
                        )  # black moves
                        if n_state in self.state_results[h] and self.pone_search(
                            n_state, h
                        ):
                            self.state_results[h][n_state] = self.color
                            return True
                elif h > 0:
                    # if h+1 > self.num_cells//2:
                    #     return False
                    for y in vm:
                        n_state_hW = self.update_state(
                            state, y, self.opp_color, h - 1
                        )  # hit the hidden stone
                        if n_state_hW not in self.state_results[h - 1]:
                            continue
                        n_state_B = self.update_state(
                            state, y, self.color, h
                        )  # black plays
                        # check if black won
                        if (
                            n_state_B in self.state_results[h]
                            and self.pone_search(n_state_hW, h - 1)
                            and self.pone_search(n_state_B, h)
                        ):
                            self.state_results[h][n_state_B] = self.color
                            self.state_results[h - 1][n_state_hW] = self.color
                            return True
        return False

    def update_state(self, state: tuple, loc: int, color: str, h: int) -> list:
        """
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
        """
        new_state = list(copy.deepcopy(state))
        new_state[loc] = color
        new_state = tuple(new_state)
        if self.check_state(new_state, h):
            return new_state
        return ()

    def check_state(self, state: tuple, h: int) -> str:
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

    def turn_info(self, state: tuple, h: int) -> str:
        """
        Checks which players turn is it given the state and
        the number of hidden stones.

        Args:
            - state:    State to check the legality.
            - h:        Number of hidden stones.
        Returns:
            - C_PLAYER1/C_PLAYER2   Player whose turn it is.
        """
        count_b = state.count(C_PLAYER1)
        count_w = state.count(C_PLAYER2) + h
        if count_b <= count_w:
            return C_PLAYER1
        else:
            return C_PLAYER2

    def find_positions(self) -> None:
        """
        Find all the legal positions, examine every position
        in depth for prob 1 wins for players. It fills the dictionary
        'state results'.
        """
        tot = 0
        tot1 = 0
        tot2 = 0
        for e in pit(range(self.num_cells), color="red"):  # empty cells
            for h in pit(range(self.num_cells // 2), color="green"):  # hidden cells
                time1 = time()
                if e + h >= self.num_cells:
                    continue
                states = self.all_states(e + h)
                time1_end = time()
                for s in pit(range(len(states)), color="blue"):
                    state = states[s]
                    try:
                        res = self.state_results[h][state]
                    except:
                        res = self.is_legal(state, h)
                    if res:  # if res is legal
                        self.state_results[h][state] = res
                        if self.pone_search(state, h):
                            self.state_results[h][state] = self.color
                            self.prob1_wins.append((state, h))  # is it needed?
                time2_end = time()
                tot += time2_end - time1
                tot1 += time1_end - time1
                tot2 += time2_end - time1_end
        print("Part1\t\t\tPart2\n{}".format("=" * 45))
        print(tot1 / tot, "\t", tot2 / tot)
        print(tot1, "\t", tot2)
        print("Total time:", tot)

    def is_legal(self, state: tuple, h: int) -> str:
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
            BOARD_SIZE=[self.num_rows, self.num_cols],
            BOARD=list(state),
            legality_check=True,
            h=h,
        )
        info_sets = True
        if h > 0:
            # if partial position, check info sets
            info_sets = self.information_sets(state, h)
        # Check if the state has odd or even number of
        # empty cells.
        e = game.BOARD.count(".") - h
        if (self.num_cells - e) % 2 == 0:
            # k = 2n
            game.w_early_w = True  # check for early White win set
            gs = game.game_status()
            if gs not in "Bi" and info_sets:
                return gs
        else:
            # k = 2n + 1
            gs = game.game_status()
            game.b_early_w = True  # check for early Black win set
            if gs not in "Wi" and info_sets:
                return gs
        return False

    def information_sets(self, state: tuple, h: int) -> bool:
        """
        Checks if an information exists for the given position.

        Args:
            - state:    State to check the existing information sets.
            - h:        Number of hidden stones on the board.
        Return:
        """
        indexes_empty = [i for i, x in enumerate(state) if x == "."]
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
                    seq[list(positions[: num_b + 1])] = self.color
                    seq[list(positions[num_b + 1 :])] = self.opp_color
                    ls.append(tuple(seq))
        return ls
