'''
Strategy Verifier
-----------------
This program evaluates the performance of a strategy S for player p
against every possible strategy S' for player p', on the game DarkHex.

Strategy S is given as a {information set: [(action, probability), ...]}
Strategy S' is every legal move possible at the given game position.

The program works in a linear logic. p makes its move as long as S has
a move to make, if ANY branch stops in a tied position, the strategy is
incomplete. Otherwise the program returns the probability of the winning
for the player p.

Parameters:
    -p: player to evaluate
    -S: strategy to evaluate
'''
import sys
from collections import defaultdict
from typing import DefaultDict
from time import perf_counter
import logging
import coloredlogs

sys.path.append('../../')

from Projects.SVerify.util import calculate_turn
from Projects.SVerify.util import choose_strategy
from Projects.SVerify.util import get_game_state
from Projects.SVerify.util import greedify
from Projects.SVerify.util import save_file
from Projects.SVerify.util import play_action

from Projects.base.game.hex import pieces 
from Projects.base.game.hex import customBoard_write

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')  # Change this to DEBUG to see more info.


class LowerBoundCalculator:

    # TODO: Finish init method
    def __init__(self, game, file_name):
        self.game = game
        self.file_name = file_name
        
        self.DISCOUNT_FACTOR = 1 #0.9

        # cache the opponent's strategy
        self.STATE_VALUE_CACHE = DefaultDict(lambda: [0.0 for x in range(game['num_rows'] * game['num_cols'])]) # (cumulative value of the state)
        self.STATE_VISITED_CACHE = DefaultDict(lambda: list())


    def __calculate_lower_bound(self, game, value_db, to_play):
        '''
        Given the player and opponent strategies. Calculate the lower bound.
        '''
        player_board = game['boards'][game['player']]
        opponent_board = game['boards'][game['opponent']]

        # whose turn
        if to_play == game['player_order']:
            # player's turn
            next_to_act = 'player'
            board_to_play = player_board
            strategy = game['player_strategy']
        else:
            # opponent's turn
            next_to_act = 'opponent'
            board_to_play = opponent_board
            strategy = game['opponent_strategy']

        tot_value = 0
        # for every possible move, calculate the probability of winning
        for action, prob in strategy[board_to_play]:
            new_game, collusion = play_action(game, game[next_to_act], action)
            if new_game in [pieces.kBlackWin, pieces.kWhiteWin]:
                assert new_game == (pieces.kBlackWin if game[next_to_act] == pieces.kBlack
                                                    else pieces.kWhiteWin)
                new_value = (0 if next_to_act == 'player' else 1) * prob
            elif not collusion:
                new_value = self.__calculate_lower_bound(new_game, value_db, (to_play + 1) % 2) * prob
            else:
                new_value = self.__calculate_lower_bound(new_game, value_db, to_play) * prob
            tot_value += new_value
            value_db[opponent_board + player_board][action] = (new_value, prob)
        return tot_value
        

    def __calc_counter_strategy(self, game_state, to_play, reach_prob, depth) -> float:
        '''
        Calculate the counter strategy for the given game state. The counter
        strategy is the best possible move for the opponent given that the
        player is playing the given strategy. Uses reach probability to
        calculate the probability of winning. The assumption is that the 
        player plays with the given strategy, and reach probability captures
        the probability of player getting to the given state, opponent then
        gets its value using the probability that player gets to the state.
        Args:
            game_state: The game state to calculate the counter strategy for.
            to_play: The player to play. (0 or 1)
            depth: The current depth of the search.
        Returns:
            The expected value of the counter strategy.
        '''
        player = game_state['player']
        opponent = game_state['opponent']

        opponent_board = game_state['boards'][opponent]
        player_board = game_state['boards'][player]

        total_value = 0
        if to_play == game_state['player_order']:
            # player's turn
            strategy = game_state['player_strategy']
            for action, prob in strategy[player_board]:
                new_game, collusion = play_action(game_state, player, action)
                if new_game in [pieces.kBlackWin, pieces.kWhiteWin]:
                    value = 0 # value is 0 for player win
                else:
                    next_to_play = (to_play + 1) % 2 if not collusion else to_play
                    value = self.__calc_counter_strategy(new_game, next_to_play, reach_prob * prob, depth + 1)
                total_value += value * prob
            return total_value * (self.DISCOUNT_FACTOR ** depth)

        # opponent's turn
        prior_max = -1
        # Check if we have already calculated the value of this state
        boards_combined = opponent_board + player_board
        if boards_combined in self.STATE_VISITED_CACHE:
            mx_value = -1
            for value in self.STATE_VALUE_CACHE[opponent_board]:
                if value > mx_value:
                    mx_value = value
            if str(reach_prob) in self.STATE_VISITED_CACHE[boards_combined]:
                return mx_value * (self.DISCOUNT_FACTOR ** depth)
            else:
                prior_max = mx_value

        # If we haven't calculated the value of this state, calculate it
        self.STATE_VISITED_CACHE[boards_combined].append(str(reach_prob))

        mx_value = 0 # maximum value initialized to -1
        possible_moves = [i for i, x in enumerate(opponent_board) if x == pieces.kEmpty]
        moves_considered = 0

        # for every possible move, calculate the probability of winning
        for action in possible_moves:
            new_game, collusion = play_action(game_state, opponent, action)
            if new_game in [pieces.kBlackWin, pieces.kWhiteWin]:
                value = 1 # value is 1 for opponent win
            else:
                next_to_play = (to_play + 1) % 2 if not collusion else to_play
                value = self.__calc_counter_strategy(new_game, next_to_play, reach_prob, depth + 1)
            
            # update the cache
            # using reach probability, update the value of the state
            # current value of the state + probability of winning * reach probability
            self.STATE_VALUE_CACHE[opponent_board][action] += value * reach_prob
            # update the maximum value and the action
            
            if value > mx_value:
                mx_value = value
                total_value = value
                moves_considered = 1
            elif value == mx_value:
                total_value += value
                moves_considered += 1
        if prior_max > total_value:
            return prior_max * (self.DISCOUNT_FACTOR ** depth)
        elif moves_considered == 0:
            return total_value * (self.DISCOUNT_FACTOR ** depth)
        return (total_value / moves_considered) * (self.DISCOUNT_FACTOR ** depth)


    def run(self):
        # initialize the log
        start = perf_counter()
        log.info('Timer started')
        
        # and let the user choose one
        game_state = get_game_state(self.game)
        
        start = perf_counter()
        log.info('Timer started')

        turn = calculate_turn(game_state)

        self.__calc_counter_strategy(game_state, turn, 1, 0)
        opp_strategy = greedify(self.STATE_VALUE_CACHE)
        game_state['opponent_strategy'] = opp_strategy

        # check if the file exists already;
        value_db = defaultdict(lambda: {})
        log.debug('Value database initialized')
        log.info('Calculating values for opponent strategy')
        opp_win_prob = self.__calculate_lower_bound(game_state, value_db, turn)

        log.debug('Writing value database to file...')
        save_file(value_db, f'Data/{self.file_name}/value_db.pkl')
        
        log.debug('Writing opponent full strategy to file...')
        with open(f'Data/{self.file_name}/opp_strategy_text.txt', 'w') as f:
            for key, value in self.STATE_VALUE_CACHE.items():
                flag = False
                for i, val in enumerate(value):
                    if val > 0:
                        if not flag:
                            customBoard_write(key, game_state['num_cols'], game_state['num_rows'], f)
                            f.write('Strategy for the board {}: \n'.format(key))
                            flag = True
                        f.write('{}: {}\n'.format(i, val))
                if flag:
                    f.write('\n')

        # Report the win probability
        log.info('Win probability: {%.2f}', 1 - opp_win_prob)

        # Report the time taken
        log.info('Time took: {%.2f}', perf_counter() - start)

        # Save the opponent moves to file - opp_strategy
        save_file(opp_strategy, f'Data/{self.file_name}/opp_strategy.pkl')
