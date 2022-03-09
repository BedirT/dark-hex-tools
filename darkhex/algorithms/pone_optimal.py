# PONE (Probability One)
#
# Finds all probability one wins for the players for the game Dark Hex
# Assuming both players are playing optimally.
#
# Uses pyspiel states to traverse the tree.
#
# Uses a dictionary to save the states that are definite win states.
# These data can be used to early stop when doing search on the tree.

import math
import numpy as np
import pyspiel
import open_spiel.python.algorithms.get_all_states as pyspiel_get_all_states
from darkhex.utils.cell_state import cellState


class PoneOptimal:
    def __init__(self, num_rows, num_cols, player=0):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_cells = self.num_rows * self.num_cols

        self.player = player
        self.opponent = 1 - player

        self.game = pyspiel.load_game(f"dark_hex_ir(num_cols={num_cols},num_rows={num_rows})")
        
        self.legal_actions = {}
        self.legal_states = [{} for _ in range(self.num_cells)]
        self.empty_states = [set() for _ in range(self.num_cells+1)]  # pyspiel.State

        print("Generating all states...")
        self.setup_legal_states()   # setup the legal states
        print(self.empty_states)

    def search(self) -> list:
        """
        Find all the legal positions, examine every position
        in depth for prob 1 wins for players. It fills the dictionary
        'state results'.
        """
        for e in range(self.num_cells + 1):             # empty cells
            for h in range(math.ceil(self.num_cells / 2)):    # hidden cells
                if e + h > self.num_cells:
                    continue
                legal_states = self.empty_states[e+h]
                for info_state in legal_states:
                    res = self.legal_states[h].get(info_state, -2)
                    if res in [-1, 0, 1]:
                        res = self.pone_search(info_state, h)
                        self.legal_states[h][info_state] = res
        return self.legal_states

    def pone_search(self, info_state: str, h: int) -> bool:
        """
        Recursive algorithm to iterate through sub states and
        determine if the given position is a prob 1 win for player
        or not.

        Args:
            - info_state:   Information state to check.
            - h:            Number of hidden stones.
        Returns:
            - True/False    If given info_state and h is a definite win
        """
        status = self.legal_states[h][info_state]

        if status in [self.player, self.opponent]:
            return status

        if self.turn_info(info_state, h) != self.player:
            if self.check_state(info_state, h + 1) != -2:
                return self.pone_search(info_state, h + 1)
            return -3
        else:
            legal_actions = self.legal_actions[(info_state, h)]
            if h == 0:
                for action in legal_actions:
                    n_state = self.update_state(info_state, action, self.player, h)
                    if n_state in self.legal_states[h]:
                        if self.pone_search(n_state, h) == self.player:
                            self.legal_states[h][n_state] = self.player
                            return self.player
            elif h > 0:
                for action in legal_actions:
                    n_state_hW = self.update_state(
                        info_state, action, self.opponent, h - 1
                    )
                    if n_state_hW not in self.legal_states[h - 1]:
                        continue
                    n_state_B = self.update_state(info_state, action, self.player, h)
                    if n_state_B in self.legal_states[h]:
                        if self.pone_search(n_state_hW, h - 1) == self.player:
                            if self.pone_search(n_state_B, h) == self.player:
                                self.legal_states[h][n_state_B] = self.player
                                self.legal_states[h - 1][n_state_hW] = self.player
                                return self.player
        return -3

    def check_state(self, info_state: str, h: int) -> str:
        """If the given state is a legal state"""
        return self.legal_states[h].get(info_state, -2)

    def turn_info(self, info_state: str, h: int) -> str:
        """Which players turn is it in the given state"""
        count_player = self.count(info_state, self.player)
        count_opp = self.count(info_state, self.opponent) + h

        if self.player == 0 and count_player <= count_opp:
            return 0
        elif self.player == 1 and count_opp <= count_player:
            return 0
        return 1

    def update_state(self, info_state: str, action: int, player: int, h: int) -> list:
        """New state after the given action"""
        new_state = list(info_state)
        new_state[action] = cellState.kBlack if player == 0 else cellState.kWhite
        new_state = "".join(new_state)
        if self.check_state(new_state, h) != -2:
            return new_state
        return ""

    def setup_legal_states(self) -> None:
        """
        Setup the legal states for each h and e.
        """
        all_states = pyspiel_get_all_states.get_all_states(self.game, include_terminals=False, 
                                                   include_chance_states=False).values()
        print(f"All States gathered: {len(all_states)}")
        size_legal_action = 0
        size_legal_states = 0
        size_empty_states = 0
        for state in all_states:
            info_state = state.information_state_string(self.player)
            info_state = self.simplify_state(info_state)
            h = self._num_hidden_stones(state)
            e = self._num_empty_cells(state)
            res = -1
            if (info_state, h) not in self.legal_actions:
                self.legal_actions[(info_state, h)] = state.legal_actions(self.player)
                size_legal_action += 1
            if state.is_terminal():
                res = self.player if state.returns()[self.player] > 0 else self.opponent
            if info_state not in self.legal_states[h]:
                self.legal_states[h][info_state] = res
                size_legal_states += 1
            if info_state not in self.empty_states[e]:
                self.empty_states[e].add(info_state)
                size_empty_states += 1
            print(f"Size of legal states: {size_legal_states} | Size of legal actions: {size_legal_action} | Size of empty states: {size_empty_states}", end="\r")

    def _num_hidden_stones(self, state: pyspiel.State) -> int:
        """
        Get the number of hidden stones in the given state.

        Args:
            - state:    State to get the number of hidden stones.
        Returns:
            - int:      Number of hidden stones.
        """
        player_perspective = self.simplify_state(state.information_state_string(self.player))
        # count the known opp stones and substract from the real num of opp stones
        opp_perspective = self.simplify_state(state.information_state_string(self.opponent))
        opp_stone = cellState.kBlack if self.opponent == 0 else cellState.kWhite
        num_hidden_stones = 0
        for p_cell, o_cell in zip(player_perspective, opp_perspective):
            if o_cell == opp_stone and p_cell != opp_stone:
                num_hidden_stones += 1
        return num_hidden_stones

    def _num_empty_cells(self, state: pyspiel.State) -> int:
        """
        Get the number of empty cells in the given state.

        Args:
            - state:    State to get the number of empty cells.
        Returns:
            - int:      Number of empty cells.
        """
        player_perspective = state.information_state_string(self.player)
        return player_perspective.count('.')

    @staticmethod
    def count(info_state: str, player: int) -> int:
        """Count the player stones in the given info_state"""
        # count cellState.black_pieces if player == cellState.kBlack
        ct = 0
        for c in info_state:
            if player == 0 and c in cellState.black_pieces:
                ct += 1
            elif player == 1 and c in cellState.white_pieces:
                ct += 1
        return ct

    @staticmethod
    def simplify_state(info_state: str) -> str:
        info_state = info_state[3:]
        info_state = info_state.replace("\n", "")
        for cell in cellState.black_pieces:
            info_state = info_state.replace(cell, cellState.kBlack)
        for cell in cellState.white_pieces:
            info_state = info_state.replace(cell, cellState.kWhite)
        return info_state
        