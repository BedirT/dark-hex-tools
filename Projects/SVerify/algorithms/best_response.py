'''
Using open_spiel dark_hex implementation
to calculate best response value for a given player strategy.
'''
import sys
import pyspiel
import numpy as np
import typing
sys.path.append('../../')

from Projects.base.game.hex import pieces
from Projects.SVerify.utils.util import convert_os_strategy, convert_to_xo, get_open_spiel_state

class BestResponse:

    def __init__(self,
                 game: pyspiel.Game,
                 player: int,
                 initial_state: str,
                 num_cols: int,
                 strategy: typing.Dict[str, typing.List[typing.Tuple[int, float]]]):
        self.game = game
        self.player = player
        self.initial_state = initial_state
        self.strategy = strategy
        self.num_cols = num_cols
    

    def best_response(self):
        '''
        Calculate the best response value for the given player strategy.
        '''
        game_state = get_open_spiel_state(self.game, self.initial_state)
        self.strategy = convert_os_strategy(self.strategy, self.num_cols, self.player)
        best_response_value = self._traverse_game(game_state)

        print(f'Best response value: {best_response_value}')
        return best_response_value

    
    def _traverse_game(self, cur_state: pyspiel.State = None, depth: int = 0) -> float:
        '''
        Traverse the game tree
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
                    value = self._traverse_game(new_state, depth + 1)
                total_value += value * prob
            return total_value
        else:
            # opponents turn
            mx_value = -np.inf
            n_moves = 0 # number of moves we consider are in opponent's best moves
            legal_actions = cur_state.legal_actions()
            for action in legal_actions:
                new_state = cur_state.clone()
                new_state.apply_action(action)
                if new_state.is_terminal():
                    value = 1
                else:
                    value = self._traverse_game(new_state, depth + 1)
                if value > mx_value:
                    mx_value = value
                    n_moves = 1
                    total_value = value
                elif value == mx_value:
                    n_moves += 1
                    total_value += value
            return total_value / n_moves
            