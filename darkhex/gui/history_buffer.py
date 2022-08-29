import copy
from darkhex import logger as log


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
        self.current_info_state = []
        self.target_stack_state = []
        self.stratgen_class = stratgen_class
        self.add_history_buffer(stratgen_class)

    def add_history_buffer(self, stratgen_class):
        self.info_states.append(copy.deepcopy(stratgen_class.info_states))
        self.current_info_state.append(
            copy.deepcopy(stratgen_class.current_info_state))
        self.target_stack_state.append(
            copy.deepcopy(stratgen_class.target_stack_state))

    def rewind(self) -> None:
        """Rewinds the game."""
        if len(self.info_states) > 1:
            self.info_states.pop()
            self.current_info_state.pop()
            self.target_stack_state.pop()
        else:
            log.info("Cannot rewind any further.")
            return
        self._update_game(-1)
        log.info("Rewinded to state {}.".format(self.stratgen_class.current_info_state))

    def restart(self) -> None:
        """Restarts the game."""
        self.info_states = self.info_states[:1]
        self.current_info_state = self.current_info_state[:1]
        self.target_stack_state = self.target_stack_state[:1]
        self._update_game(0)
        log.info("Restarted the game.")

    # def search_history(self, info_state):
    #     """Search the history buffer for the given info state."""
    #     for idx, board in enumerate(self.board):
    #         if board == info_state:
    #             return idx
    #     return -1

    def _revert(self, idx):
        self.info_states = self.info_states[:idx + 1]
        self.current_info_state = self.current_info_state[:idx + 1]
        self.target_stack_state = self.target_stack_state[:idx + 1]
        self._update_game(idx)

    def _update_game(self, idx):
        self.stratgen_class.info_states = copy.deepcopy(self.info_states[idx])
        self.stratgen_class.current_info_state = copy.deepcopy(
            self.current_info_state[idx])
        self.stratgen_class.target_stack_state = copy.deepcopy(
            self.target_stack_state[idx])

    # def revert_to_state(self, idx=None, state=None):
    #     if idx and state:
    #         raise ValueError("Cannot use both idx and state.")
    #     idx = idx if idx else self.search_history(state)
    #     if idx == -1:
    #         raise ValueError("State not found.")
    #     self._revert(idx)
