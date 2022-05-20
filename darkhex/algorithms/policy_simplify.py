import math
import typing
from darkhex.utils.util import updated_board, convert_os_str, load_file
from darkhex.utils.isomorphic import isomorphic_single
import pickle
from collections import Counter
from darkhex.utils.cell_state import cellState
import numpy as np


class PolicySimplify:

    def __init__(
        self,
        initial_board: str,
        num_rows: int,
        num_cols: int,
        player: int,
        policy_type: str,
        file_path: str,
        epsilon: float, # the minimum probability of an action
        eta: float, # the maximum distance between a fraction and an action
        frac_limit: int, # the maximum number of fractions
        max_number_of_actions: int, # the maximum number of actions
        include_isomorphic: bool = True,
    ):
        self.num_cols = num_cols
        self.num_rows = num_rows
        self.p = player
        self.o = 1 - self.p
        self.max_number_of_actions = max_number_of_actions
        self.epsilon = epsilon # the minimum probability of an action

        self.frac_limit = frac_limit  # the clean fraction limit
        self.eta = eta # the difference between the probability of an
                        # action and a fraction value near it:
                        # 1/2, 1/3, 2/3, 1/4, 3/4, ...
        
        self.fraction_values = None
        if self.eta > 0 and self.frac_limit > 0:
            self.fraction_values = self._calculate_fractions()
            print(f"Fraction values: {self.fraction_values}")

        # todo: make the file name dynamic
        if policy_type == "mccfr":
            with open(file_path, "rb") as f:
                solver = pickle.load(f)
            self.policy = solver.average_policy()
        else:
            raise NotImplementedError(
                f"Policy type {policy_type} not implemented.")

        self.all_states = load_file(
            f"darkhex/data/state_data/{num_rows}x{num_cols}.pkl")

        # Perform Checks to see if initial values are valid
        if not is_valid_board(initial_board, num_rows, num_cols):
            raise ValueError("Invalid initial board")

        self.info_states = {}

        self.iterate_board(initial_board)

    def _calculate_fractions(self):
        """
        Calculate the fraction values.
        """
        fractions = set()
        for n in range(1, self.frac_limit + 1):
            for k in range(1, n):
                frac = k / n
                fractions.add(frac)
        return sorted(fractions)        

    def iterate_board(self, board) -> None:
        """Iterate the board"""
        new_boards = self.set_new_boards(board)
        if not new_boards:
            return
        actions = self.info_states[board].keys()
        collusion_possible = self._is_collusion_possible(board)
        for action in actions:
            new_board = new_boards[f"{action}{self.p}"]
            if not self._is_terminal(new_board) and \
               new_board not in self.info_states:
                self.iterate_board(new_board)
            if collusion_possible:
                new_board = new_boards[f"{action}{self.o}"]
                if not self._is_terminal(new_board) and \
                   new_board not in self.info_states:
                    self.iterate_board(new_board)

    def set_new_boards(self, board):
        action_probs = self.get_action_probs(board)
        if action_probs is None:
            return {}
        action_probs = self.fractionize(action_probs)
        self.info_states[board] = action_probs
        new_boards = {}
        for a in self.info_states[board].keys():
            o_color = "o" if self.p == 0 else "x"
            p_color = "x" if self.p == 0 else "o"
            new_board = updated_board(board, a, o_color, self.num_rows,
                                      self.num_cols)
            new_board_2 = updated_board(board, a, p_color, self.num_rows,
                                        self.num_cols)
            if new_board:
                new_boards[f"{a}{self.o}"] = new_board
            if new_board_2:
                new_boards[f"{a}{self.p}"] = new_board_2
        return new_boards

    def get_action_probs(self, board):
        """Get action probabilities for the info_states."""
        state = self.state_for_board(board)
        if state is None:
            return None
        action_probs_init = self.policy.action_probabilities(state)
        # only n actions per state is possible, so keep max n
        # actions and their probabilities, and renormalize the probabilities
        # to sum to 1. All actions must have probabilities greater than epsilon
        # to be considered.
        legal_actions = state.legal_actions(self.p)
        # print(f"Legal actions: {legal_actions}")
        action_probs = {
            i: action_probs_init[i]
            for i in legal_actions
            if action_probs_init[i] > self.epsilon
        }
        if not action_probs:
            # No actions larger than epsilon
            # Choose a single action with the highest probability
            pos_actions = [
                i for i in legal_actions
                if action_probs_init[i] == max(action_probs_init.values())
            ]
            action = np.random.choice(pos_actions)
            action_probs = {action: 1.0}
        sorted_action_probs = sorted(action_probs.items(),
                                     key=lambda x: x[1],
                                     reverse=True)
        sorted_action_probs = sorted_action_probs[:self.max_number_of_actions]
        action_probs = {k: v for k, v in sorted_action_probs}
        total = sum(action_probs.values())
        action_probs = {k: v / total for k, v in action_probs.items()}
        # print(f"Action probs: {action_probs}")

        return action_probs

    def fractionize(self, action_probs):
        """
        Fractionize the action probabilities.

        For a given action probability, find if "all" action probabilities
        are within eta distance of a fraction value. If so, return the
        fraction values. If not, return the original action probabilities.
        """
        if not self.fraction_values:
            return action_probs
        fraction_probs = {}
        for action, prob in action_probs.items():
            for frac in self.fraction_values:
                if abs(frac - prob) <= self.eta:
                    if action not in fraction_probs:
                        fraction_probs[action] = frac
                    else:
                        # if the fraction is already in the dict,
                        # get the closest fraction value
                        if abs(prob - fraction_probs[action]) > \
                           abs(prob - frac):
                            fraction_probs[action] = frac
        if len(fraction_probs) == len(action_probs):
            if sum(fraction_probs.values()) == 1:
                if action_probs != fraction_probs:
                    print(f"Converted to fractions: {action_probs} | {fraction_probs}")
                return fraction_probs
            else:
                print(f"Failed to convert to fractions: {action_probs} | {fraction_probs}")
        return action_probs

    def state_for_board(self, board):
        """
        Get the state for the board.
        """
        board = convert_os_str(board, self.num_cols, self.p)
        # print(self.all_states)
        if board not in self.all_states:
            # illegal
            return None
        return self.all_states[board]

    def _is_collusion_possible(self, board) -> bool:
        """
        Check if a collusion is possible.
        """
        # Get the number of cellState on the board.
        count = Counter(board)
        if self.p == 1:
            player_pieces = sum(
                [s for x, s in count.items() if x in cellState.white_pieces])
            opponent_pieces = sum(
                [s for x, s in count.items() if x in cellState.black_pieces])
            return opponent_pieces <= player_pieces
        player_pieces = sum(
            [s for x, s in count.items() if x in cellState.black_pieces])
        opponent_pieces = sum(
            [s for x, s in count.items() if x in cellState.white_pieces])
        return opponent_pieces < player_pieces

    def _is_terminal(self, board_state):
        """
        Check if the game is over.

        - board_state: The current board state.
        """
        if (board_state.count(cellState.kBlackWin) +
                board_state.count(cellState.kWhiteWin) > 0):
            return True
        ct = Counter(board_state)
        empty_cells = ct[cellState.kEmpty]
        if self.p == 0:
            opponent_pieces = sum(
                [s for x, s in ct.items() if x in cellState.white_pieces])
            player_pieces = sum(
                [s for x, s in ct.items() if x in cellState.black_pieces])
            if opponent_pieces + empty_cells == player_pieces:
                return True
        else:
            opponent_pieces = sum(
                [s for x, s in ct.items() if x in cellState.black_pieces])
            player_pieces = sum(
                [s for x, s in ct.items() if x in cellState.white_pieces])
            if opponent_pieces + empty_cells == player_pieces + 1:
                return True
        return False


def is_valid_board(board: str, num_rows: int, num_cols: int) -> bool:
    """Check if the given board is valid."""
    # TODO: Complete this function.
    if len(board) != num_rows * num_cols:
        return False
    return True
