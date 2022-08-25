import copy

class gameBuffer:
    """History buffer for the game to use for rewind and restart."""

    def __init__(self, initial_board: str, num_rows: int, num_cols: int,
                 player: int, include_isomorphic: bool, stratgen_class) -> None:
        self.game_info = {
            "num_rows": num_rows,
            "num_cols": num_cols,
            "player": player,
            "isomorphic": include_isomorphic,
            "initial_board": initial_board,
        }
        self.info_states = []
        self.moves_and_boards = []
        self.board = []
        self.move_stack = []
        self.given_inputs = []
        self.stratgen_class = stratgen_class
        self.add_history_buffer(stratgen_class)

    def add_history_buffer(self, stratgen_class, given_input=None):
        self.info_states.append(copy.deepcopy(stratgen_class.info_states))
        self.moves_and_boards.append(copy.deepcopy(stratgen_class.moves_and_boards))
        self.board.append(copy.deepcopy(stratgen_class.board))
        self.move_stack.append(copy.deepcopy(stratgen_class.move_stack))
        if given_input:
            self.given_inputs.append(given_input)

    def rewind(self) -> str:
        """Rewinds the game."""
        if len(self.info_states) > 1:
            self.info_states.pop()
            self.moves_and_boards.pop()
            self.board.pop()
            self.move_stack.pop()
            self.given_inputs.pop()
        else:
            return "Cannot rewind anymore.\n"
        self._update_game(-1)
        return "Rewinded to the previous state.\n"

    def restart(self) -> str:
        """Restarts the game."""
        self.info_states = self.info_states[:1]
        self.moves_and_boards = self.moves_and_boards[:1]
        self.board = self.board[:1]
        self.move_stack = self.move_stack[:1]
        self.given_inputs = []
        self._update_game(0)
        return "Restarted the game.\n"

    def search_history(self, info_state):
        """Search the history buffer for the given info state."""
        for idx, board in enumerate(self.board):
            if board == info_state:
                return idx
        return -1

    def _revert(self, idx):
        self.info_states = self.info_states[:idx + 1]
        self.moves_and_boards = self.moves_and_boards[:idx + 1]
        self.board = self.board[:idx + 1]
        self.move_stack = self.move_stack[:idx + 1]
        self.given_inputs = self.given_inputs[:idx + 1]
        self._update_game(idx)

    def _update_game(self, idx):
        self.stratgen_class.info_states = copy.deepcopy(self.info_states[idx])
        self.stratgen_class.moves_and_boards = copy.deepcopy(
            self.moves_and_boards[idx])
        self.stratgen_class.board = copy.deepcopy(self.board[idx])
        self.stratgen_class.move_stack = copy.deepcopy(self.move_stack[idx])

    def revert_to_state(self, idx=None, state=None):
        if idx and state:
            raise ValueError("Cannot use both idx and state.")
        if idx:
            self._revert(idx)
        elif state:
            idx = self.search_history(state)
            if idx != -1:
                self._revert(idx)
            else:
                raise ValueError("State not found.")