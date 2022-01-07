'''
Using open_spiel dark_hex implementation
to calculate best response value for a given player strategy.
'''
from collections import defaultdict
import re
import sys
import pyspiel
import numpy as np
import typing
sys.path.append('../../')

from Projects.base.game.hex import pieces
from Projects.SVerify.utils.util import convert_os_strategy, convert_to_xo, get_open_spiel_state, save_file

class BestResponse:

    def __init__(self,
                 game: pyspiel.Game,
                 player: int,
                 initial_state: str,
                 num_cols: int,
                 strategy: typing.Dict[str, typing.List[typing.Tuple[int, float]]],
                 file_path: str = 'Data/post_process/test/opponent_strategy.pkl'):
        self.game = game
        self.player = player
        self.initial_state = initial_state
        self.strategy = strategy
        self.num_cols = num_cols
        self.file_path = file_path

        self.opponent_strategy = defaultdict(lambda: {})
        
        self.tau_s = defaultdict(lambda: 0.0)


    def best_response(self):
        '''
        Calculate the best response value for the given player strategy.
        '''
        game_state = get_open_spiel_state(self.game, self.initial_state)
        self.strategy = convert_os_strategy(self.strategy, self.num_cols, self.player)
        best_response_value = self._generate_response_strategy(game_state)

        print(f'Best response value: {best_response_value}')

        # write the opponent strategy to a file
        save_file(self.opponent_strategy, self.file_path)

        return best_response_value

    
    def _generate_response_strategy(self, 
                                    cur_state: pyspiel.State = None, 
                                    depth: int = 0,
                                    reach_prob: float = 0.0) -> float:
        '''
        Traverse the game tree, calculate the value for each state, and generate a
        policy for the opponent.

        When we evaluate a state for the opponent, we want to maximize the value of the state
        which is v(s). Since we know the opponent strategy, we have the power to calculate
        exact values for each state. We use counterfactual reach probabilities to calculate
        the probability of reaching each state, afterwards the opponent is always choosing
        the state with the highest value only. (single action for each state).

        v(s) = \tau(s) * max_a v(s,a)
    
        where \tau(s) is the probability of reaching the state s, and v(s,a) is the value
        of the state s after action a. 
        \tau(s) is always the maximum possible probability of reaching the state s.

        Returns the best response value for the given player strategy.
        Updates the opponent strategy.
        '''
        cur_player = cur_state.current_player()

        total_value = 0
        if cur_player == self.player:
            # players turn
            info_state = cur_state.information_state_string(self.player)
            for action, prob in self.strategy[info_state]:
                new_state = cur_state.clone()
                new_state.apply_action(action)
                if new_state.is_terminal():
                    value = 0 # new_state.returns()[cur_player]
                else:
                    value = self._generate_response_strategy(new_state, depth + 1, reach_prob * prob)
                total_value += value * prob
            return total_value
        else:
            # opponents turn
            mx_value = -2
            info_state = cur_state.information_state_string(cur_player)
            # check tau(s) update if the old value is smaller than the new value
            if self.tau_s[info_state] < reach_prob:
                self.tau_s[info_state] = reach_prob
            else:
                reach_prob = self.tau_s[info_state]
            legal_actions = cur_state.legal_actions()
            for action in legal_actions:
                new_state = cur_state.clone()
                new_state.apply_action(action)
                if new_state.is_terminal():
                    value = 1
                    mx_value = value
                    self.opponent_strategy[info_state] = [(action, 1)]
                    break
                else:
                    value = self._generate_response_strategy(new_state, depth + 1, reach_prob)
                if mx_value < value:
                    mx_value = value
                    # update the opponent strategy
                    self.opponent_strategy[info_state] = [(action, 1)]
            if mx_value == -2:
                raise Exception('mx_value is -2')
            return mx_value * reach_prob
            