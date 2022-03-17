import math
import typing
from darkhex.utils.util import updated_board, convert_os_str, load_file
from darkhex.utils.isomorphic import isomorphic_single
import pickle
from collections import Counter
from darkhex.utils.cell_state import cellState


class PolicySimplify:
    def __init__(
        self,
        game,
        initial_board: str,
        num_rows: int,
        num_cols: int,
        player: int,
        include_isomorphic: bool = True,
    ):
        self.game = game
        self.num_cols = num_cols
        self.num_rows = num_rows
        self.p = player
        self.o = 1 - self.p

        
        with open("../open_spiel/tmp/dark_hex_mccfr_2x2/dark_hex_mccfr_solver", "rb") as f:
            solver = pickle.load(f) 
        self.policy = solver.average_policy()

        self.all_states = load_file("darkhex/data/state_data2x2.pkl")

        # Perform Checks to see if initial values are valid
        if not is_valid_board(initial_board, num_rows, num_cols):
            raise ValueError("Invalid initial board")
  
        self.info_states = {}
        
        self.iterate_board(initial_board)

    def iterate_board(self, board) -> None:
        """Iterate the board"""
        new_boards = self.set_new_boards(board)
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
        self.info_states[board] = self.get_action_probs(board)
        new_boards = {}
        for a in self.info_states[board].keys():
            o_color = "o" if self.p == 0 else "x"
            p_color = "x" if self.p == 0 else "o"
            new_board = updated_board(
                board, a, o_color, self.num_rows, self.num_cols
            )
            new_board_2 = updated_board(
                board, a, p_color, self.num_rows, self.num_cols
            )
            if new_board:
                new_boards[f"{a}{self.o}"] = new_board
            if new_board_2:
                new_boards[f"{a}{self.p}"] = new_board_2 
        return new_boards

    def get_action_probs(self, board):
        """Get action probabilities for the info_states."""
        state = self.state_for_board(board)
        action_probs = self.policy.action_probabilities(state)
        # only two actions per state is possible, so keep max 2
        # actions and their probabilities, and renormalize the probabilities
        # to sum to 1. All actions must have probabilities greater than 0.09
        # to be considered.
        legal_actions = state.legal_actions(self.p)
        print(f"Legal actions: {legal_actions}")
        action_probs = {
            i: action_probs[i]
            for i in legal_actions
            if action_probs[i] > 0.09
        }
        sorted_action_probs = sorted(action_probs.items(), key=lambda x: x[1], reverse=True)
        sorted_action_probs = sorted_action_probs[:2] 
        action_probs = {k: v for k, v in sorted_action_probs}
        total = sum(action_probs.values())
        action_probs = {k: v / total for k, v in action_probs.items()}
        print(f"Action probs: {action_probs}")
        
        return action_probs

    def state_for_board(self, board):
        """
        Get the state for the board.
        """
        board = convert_os_str(board, self.num_cols, self.p)
        # print(self.all_states)
        return self.all_states[board]

    def _is_collusion_possible(self, board) -> bool:
        """
        Check if a collusion is possible.
        """
        # Get the number of cellState on the board.
        count = Counter(board)
        if self.p == 1:
            player_pieces = sum(
                [s for x, s in count.items() if x in cellState.white_pieces]
            )
            opponent_pieces = sum(
                [s for x, s in count.items() if x in cellState.black_pieces]
            )
            return opponent_pieces <= player_pieces
        player_pieces = sum(
            [s for x, s in count.items() if x in cellState.black_pieces]
        )
        opponent_pieces = sum(
            [s for x, s in count.items() if x in cellState.white_pieces]
        )
        return opponent_pieces < player_pieces

    def _is_terminal(self, board_state):
        """
        Check if the game is over.

        - board_state: The current board state.
        """
        if (
            board_state.count(cellState.kBlackWin)
            + board_state.count(cellState.kWhiteWin)
            > 0
        ):
            return True
        ct = Counter(board_state)
        empty_cells = ct[cellState.kEmpty]
        if self.p == 0:
            opponent_pieces = sum(
                [s for x, s in ct.items() if x in cellState.white_pieces]
            )
            player_pieces = sum(
                [s for x, s in ct.items() if x in cellState.black_pieces]
            )
            if opponent_pieces + empty_cells == player_pieces:
                return True
        else:
            opponent_pieces = sum(
                [s for x, s in ct.items() if x in cellState.black_pieces]
            )
            player_pieces = sum(
                [s for x, s in ct.items() if x in cellState.white_pieces]
            )
            if opponent_pieces + empty_cells == player_pieces + 1:
                return True
        return False


def is_valid_board(board: str, num_rows: int, num_cols: int) -> bool:
    """Check if the given board is valid."""
    # TODO: Complete this function.
    if len(board) != num_rows * num_cols:
        return False
    return True
