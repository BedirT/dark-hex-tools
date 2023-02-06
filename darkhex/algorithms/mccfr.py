import typing
import numpy as np
import pyspiel

REGRET_IDX = 0
AVG_POLICY_IDX = 1


class MCCFRBase:

    def __init__(self, game: pyspiel.Game) -> None:
        self._game = game
        self._info_states = {}
        self._num_players = game.num_players()
        self._initial_fraction = 1e6  # starting value for the regrets

    def _get_info_state(self, info_state: str,
                        num_legal_actions: int) -> typing.List[np.array]:
        """
        Returns the info state dictionary for the given info state.
        If the info state is not in the dictionary, it is initialized with initial_fraction.

        Args:
            info_state (str): The info state.
            num_legal_actions (int): The number of legal actions for the info state.
        Returns:
            list: The info state list.
        """
        if info_state not in self._info_states:
            self._info_states[info_state] = [
                np.zeros(num_legal_actions) / self._initial_fraction,
                np.zeros(num_legal_actions) / self._initial_fraction,
            ]
        return self._info_states[info_state]

    def _update_avg_policy(self, info_state: str, action_idx: int,
                           value_to_add: float) -> None:
        """
        Updates the average policy for the given info state and action.
        Args:
            info_state (str): The info state.
            action_idx (int): The action index.
            value_to_add (float): The value to add to the average policy.
        """
        info_state_list = self._get_info_state(info_state, self._num_players)
        info_state_list[AVG_POLICY_IDX][action_idx] += value_to_add

    def _update_regret(self, info_state: str, action_idx: int,
                       value_to_add: float) -> None:
        """
        Updates the regret for the given info state and action.
        Args:
            info_state (str): The info state.
            action_idx (int): The action index.
            value_to_add (float): The value to add to the regret.
        """
        info_state_list = self._get_info_state(info_state, self._num_players)
        info_state_list[REGRET_IDX][action_idx] += value_to_add

    def _regret_matching(self, regrets: np.array,
                         num_legal_actions: int) -> np.array:
        """
        Performs regret matching on the given regrets. Regret matching only considers
        positive regrets and updates the negative regrets to 0.
        Args:
            regrets (np.array): The regrets.
            num_legal_actions (int): The number of legal actions for the info state.
        Returns:
            np.array: The regrets after regret matching.
        """
        regrets[regrets < 0] = 0.
        regret_sum = regrets.sum()
        if regret_sum > 0:
            regrets /= regret_sum
        else:
            regrets[:] = 1. / num_legal_actions
        return regrets
