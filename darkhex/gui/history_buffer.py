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
        self.actions_and_states = []
        self.board = []
        self.action_stack = []
        self.action_stack_action_history = []
        self.given_inputs = []
        self.stratgen_class = stratgen_class
        self.add_history_buffer(stratgen_class)

    def add_history_buffer(self, stratgen_class, given_input=None):
        self.info_states.append(copy.deepcopy(stratgen_class.info_states))
        self.actions_and_states.append(
            copy.deepcopy(stratgen_class.actions_and_states))
        self.board.append(copy.deepcopy(stratgen_class.board))
        self.action_stack.append(copy.deepcopy(stratgen_class.action_stack))
        self.action_stack_action_history.append(
            copy.deepcopy(stratgen_class.action_stack_action_history))

        if given_input:
            self.given_inputs.append(given_input)

    def rewind(self) -> str:
        """Rewinds the game."""
        if len(self.info_states) > 1:
            self.info_states.pop()
            self.actions_and_states.pop()
            self.board.pop()
            self.action_stack.pop()
            self.action_stack_action_history.pop()
            self.given_inputs.pop()
        else:
            return "Cannot rewind anymore.\n"
        self._update_game(-1)
        return "Rewinded to the previous state.\n"

    def restart(self) -> str:
        """Restarts the game."""
        self.info_states = self.info_states[:1]
        self.actions_and_states = self.actions_and_states[:1]
        self.board = self.board[:1]
        self.action_stack = self.action_stack[:1]
        self.action_stack_action_history = self.action_stack_action_history[:1]
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
        self.actions_and_states = self.actions_and_states[:idx + 1]
        self.board = self.board[:idx + 1]
        self.action_stack = self.action_stack[:idx + 1]
        self.action_stack_action_history = self.action_stack_action_history[:idx
                                                                            + 1]
        self.given_inputs = self.given_inputs[:idx + 1]
        self._update_game(idx)

    def _update_game(self, idx):
        self.stratgen_class.info_states = copy.deepcopy(self.info_states[idx])
        self.stratgen_class.actions_and_states = copy.deepcopy(
            self.actions_and_states[idx])
        self.stratgen_class.board = copy.deepcopy(self.board[idx])
        self.stratgen_class.action_stack = copy.deepcopy(self.action_stack[idx])
        self.stratgen_class.action_stack_action_history = copy.deepcopy(
            self.action_stack_action_history[idx])

    def revert_to_state(self, idx=None, state=None):
        if idx and state:
            raise ValueError("Cannot use both idx and state.")
        idx = idx if idx else self.search_history(state)
        if idx == -1:
            raise ValueError("State not found.")
        self._revert(idx)
