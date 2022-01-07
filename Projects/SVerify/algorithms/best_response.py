'''
Using open_spiel dark_hex implementation
to calculate best response value for a given player strategy.
'''
from collections import defaultdict
import re
import sys
from numpy.core.fromnumeric import argmax
import pyspiel
import numpy as np
import typing
sys.path.append('../../')

from Projects.SVerify.utils.util import convert_os_strategy, get_open_spiel_state, save_file

import logging
import coloredlogs

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')  # Change this to DEBUG to see more info.

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

        self.opp_state_value_cache = defaultdict(lambda: defaultdict(lambda: 0))
        self.tau_s = defaultdict(lambda: 0.0)


    def best_response(self):
        '''
        Calculate the best response value for the given player strategy.
        '''
        game_state = get_open_spiel_state(self.game, self.initial_state)
        self.strategy = convert_os_strategy(self.strategy, self.num_cols, self.player)
        self._generate_response_values(game_state.clone())

        # traverse the calculated values and generate the best response strategy
        self._generate_response_strategy()

        # calculate the best response value
        self.strategies = {
            self.player: self.strategy,
            1 - self.player: self.opponent_strategy
        }
        br_value = self._calculate_br_value(game_state)

        log.info(f'Best response value: {br_value}')

        # write the opponent strategy to a file
        save_file(self.opponent_strategy, self.file_path)

        return br_value

    
    def _generate_response_values(self, 
                                    cur_state: pyspiel.State, 
                                    depth: int = 0,
                                    reach_prob: float = 1.0) -> float:
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
        info_state = cur_state.information_state_string()

        total_value = 0
        if cur_player == self.player:
            # players turn
            for action, prob in self.strategy[info_state]:
                new_state = cur_state.clone()
                new_state.apply_action(action)
                if new_state.is_terminal():
                    value = 0 # new_state.returns()[cur_player]
                else:
                    value = self._generate_response_values(new_state, depth + 1, reach_prob * prob)
                total_value += value * prob
            return total_value
        else:
            # opponents turn
            # check tau(s) update if the old value is smaller than the new value
            # ? Should tau be updated for each state?
            if self.tau_s[info_state] < reach_prob:
                self.tau_s[info_state] = reach_prob
            elif self.tau_s[info_state] > reach_prob:
                reach_prob = self.tau_s[info_state]
            legal_actions = cur_state.legal_actions()
            for i, action in enumerate(legal_actions):
                new_state = cur_state.clone()
                new_state.apply_action(action)
                if new_state.is_terminal():
                    value = 1
                else:
                    value = self._generate_response_values(new_state, depth + 1, reach_prob)
                # update the value cache
                # ? Should we save with or without reach probability?
                self.opp_state_value_cache[info_state][action] += value
            return max(self.opp_state_value_cache[info_state]) * reach_prob


    def _generate_response_strategy(self):
        '''
        Uses the generated opponent information state-action values, and
        the player's strategy to generate the best response strategy.
        '''
        best_response_strategy = {}
        for info_state in self.opp_state_value_cache:
            # get the best action for the state from the opponent's value cache
            for action, value in self.opp_state_value_cache[info_state].items():
                if value == max(self.opp_state_value_cache[info_state].values()):
                    best_response_strategy[info_state] = [(action, 1.0)]
                    break
        self.opponent_strategy = best_response_strategy


    def _calculate_br_value(self, cur_state: pyspiel.State) -> float:
        '''
        Calculate the best response value for the given player strategy and
        calculated opponent strategy.
        '''
        br_value = 0
        cur_player = cur_state.current_player()
        info_state = cur_state.information_state_string()
        for action, prob in self.strategies[cur_player][info_state]:
            new_state = cur_state.clone()
            new_state.apply_action(action)
            if new_state.is_terminal():
                value = 1 if cur_player != self.player else 0
            else:
                value = self._calculate_br_value(new_state)
            br_value += value * prob
        return br_value