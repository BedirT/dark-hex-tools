import typing

import pyspiel


class PONE:
    """
    pONE implementation. Uses pyspiel. Calculates the definite
    win states for either players by traversing full tree.
    Saves the states in a list that is encoded by their information
    state.
    """

    def __init__(self, game: pyspiel.Game, num_rows: int, num_cols: int) -> None:
        # ? maybe initialize game here instead of taking it as a parameter
        self.game = game
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_cells = num_rows * num_cols

    def get_definite_win_states(self) -> typing.List[typing.List[typing.List[int]]]:
        """
        Returns a list of states that are definite win states.

        Calls the recursive function _get_definite_win_states to
        traverse the tree and save the states in a list.
        """
        definite_wins = []
        initial_state = self.game.new_initial_state()
        self._get_definite_win_states(initial_state, definite_wins)
        return definite_wins

    def _get_definite_win_states(
        self,
        state: pyspiel.State,
        definite_wins: typing.List[typing.List[typing.List[int]]],
    ) -> None:
        """
        Recursive function that traverses the game in a dfs like order and
        checks if a state is a definite win state.
        """
        cur_player = state.current_player()
        if state.is_terminal():
            definite_wins[cur_player].append(state.information_state_string())
            return
        definite_win_state = False
        for action in state.legal_actions():
            new_state = state.clone()
            new_state.apply_action(action)
            if self.instant_definite_win(new_state):
                definite_wins[cur_player].append(new_state.information_state_string())
                definite_win_state = True
            else:
                self._get_definite_win_states(new_state, definite_wins)
        return definite_win_state

    def instant_definite_win(self, state: pyspiel.State) -> bool:
        """
        Checks if a state is a definite win state.
        """
        cur_player = state.current_player()
        if state.is_terminal():
            return state.rewards()[cur_player] > 0
        for action in state.legal_actions():
            new_state = state.clone()
            new_state.apply_action(action)
            if self.instant_definite_win(new_state):
                return True
        return False
