"""
Using open_spiel dark_hex implementation
to calculate best response value for a given player strategy.
"""
import typing
from collections import defaultdict

import pyspiel
from darkhex.utils.util import (
    convert_os_strategy, 
    get_open_spiel_state, 
    greedify, 
    save_file,
    load_file
)


class BestResponse:
    def __init__(
        self,
        game: pyspiel.Game,
        strategy_player: int,
        initial_state: str,
        num_cols: int,
        strategy: typing.Dict[str, typing.List[typing.Tuple[int, float]]],
        file_path: str,
    ):
        self.game = game
        self.s_player = strategy_player
        self.br_player = 1 - strategy_player
        self.initial_state = initial_state
        self.strategy = strategy
        self.num_cols = num_cols
        self.file_path = file_path

        self.opp_state_value_cache = defaultdict(lambda: defaultdict(lambda: 0))
        self.full_game_cache = defaultdict(lambda: list())

    def _generate_response_strategy(
        self, cur_state: pyspiel.State, reach_prob: float = 1.0
    ) -> float:
        """
        Each possible information set is observed and the response value for the
        opponent is calculated recursively.

        The response value is the cumulative value of the state in perspective
        of the opponent. Backward induction is used to calculate the response
        values with the help of counterfactual reach probabilities.

        This method works for games like dark_hex_ir due to the fact that the
        opponent strategy will be greedified and the abstractions used; the
        board and the self actions are all known and sufficient to calculate
        the response value.

        When we evaluate a state for the opponent, we want to maximize the value of the state
        which is v(s). Since we know the opponent strategy, we have the power to calculate
        exact values for each state. We use counterfactual reach probabilities to calculate
        the probability of reaching each state, afterwards the opponent is always choosing
        the state with the highest value only. (single action for each state).

        v(s) = tau(s) * max_a q(s,a)

        where tau(s) is the probability of reaching the state s, and q(s,a) is the value
        of the state s after action a.
        tau(s) is always the maximum possible probability of reaching the state s.

        Updates the opponent strategy based on the calculated values.
        """
        cur_player = cur_state.current_player()
        info_state = cur_state.information_state_string()

        if cur_player == self.s_player:
            # strategy players turn (min player)
            total_value = 0
            # print(self.strategy, self.num_cols)
            for action, prob in self.strategy[info_state]:
                new_state = cur_state.child(action)
                if new_state.is_terminal():
                    value = 0 if new_state.returns()[self.s_player] == 1 else 1
                else:
                    value = self._generate_response_strategy(
                        new_state, reach_prob * prob
                    )
                total_value += value * prob
            return total_value
        # best response players turn (max player)
        mx_value = -1e9
        for action in cur_state.legal_actions():
            new_state = cur_state.child(action)
            if new_state.is_terminal():
                value = 0 if new_state.returns()[self.s_player] == 1 else 1
            else:
                value = self._generate_response_strategy(new_state, reach_prob)
            self.opp_state_value_cache[info_state][action] += value * reach_prob
            if value > mx_value:
                mx_value = value
        # ? NOT SURE IF THIS SHOULD BE MULTIPLIED BY THE REACH PROBABILITY
        return mx_value * reach_prob

    def _calculate_br_value(self, cur_state: pyspiel.State) -> float:
        """
        Calculate the best response value for the given player strategy and
        calculated opponent strategy.
        """
        br_value = 0
        cur_player = cur_state.current_player()
        info_state = cur_state.information_state_string()
        for action, prob in self.strategies[cur_player][info_state]:
            new_state = cur_state.child(action)
            if new_state.is_terminal():
                value = 1 if new_state.returns()[self.br_player] == 1 else 0
            else:
                value = self._calculate_br_value(new_state)
            br_value += value * prob
        return br_value

    def best_response(self):
        """
        Calculate the best response value for the given player strategy.
        """
        game_state = get_open_spiel_state(self.game, self.initial_state)
        
        # Get opponent strategy
        self._generate_response_strategy(game_state)

        # Greeedify the opponent strategy (single move allowed for each state)
        self.opponent_strategy = greedify(self.opp_state_value_cache)

        # self.opponent_strategy = load_file(self.file_path)

        # calculate the best response value
        self.strategies = {
            self.s_player: self.strategy,
            self.br_player: self.opponent_strategy,
        }
        br_value = 1 - self._calculate_br_value(game_state)

        # write the opponent strategy to a file
        save_file(self.opponent_strategy, self.file_path)

        return br_value
