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
        self.state_oracle: typing.Dict[str, int] = {}

    def get_definite_win_states(self) -> typing.List[str]:
        """
        Returns a list of states that are definite win states.

        Calls the recursive function _get_definite_win_states to
        traverse the tree and save the states in a list.
        """
        initial_state = self.game.new_initial_state()
        self.definite_win_from_state(initial_state)
        return list(self.state_oracle.keys())

    def definite_win_from_state(self, state: pyspiel.State) -> int:
        """
        Checks if a state is a definite win state.

        Returns 0 if the state is a definite win for player 0, 1 if it is
        a definite win for player 1, and -1 otherwise.
        """
        cur_player = state.current_player()
        best_case = cur_player - 1
        for action in state.legal_actions():
            info_state = state.information_state_string()
            new_state = state.clone()
            new_state.apply_action(action)
            if new_state.is_terminal():
                self.state_oracle[info_state] = cur_player
                return cur_player
            oracle_val = self.definite_win_oracle(new_state)
            if oracle_val == cur_player:
                return cur_player
            def_win = self.definite_win_from_state(new_state)
            if def_win == cur_player:
                self.state_oracle[info_state] = cur_player
                return cur_player
            if def_win == -1:
                best_case = -1
        return best_case

    def definite_win_oracle(self, state: pyspiel.State) -> int:
        """
        Returns the value of the oracle for a state.

        The oracle is the value of the state for the current player
        if the state is a definite win state for that player.
        """
        if state.information_state_string() in self.state_oracle:
            return self.state_oracle[state.information_state_string()]
        return -1
