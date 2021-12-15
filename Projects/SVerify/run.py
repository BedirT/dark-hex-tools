# pylint: disable=consider-using-f-string
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
import os
from collections import defaultdict
from typing import DefaultDict
from time import perf_counter
import pickle
import logging
import coloredlogs

import dill
sys.path.append('../../')

from Projects.SVerify.util import calculate_turn, choose_strategy, get_game_state, greedify, play_action, save_file
from Projects.base.game.hex import pieces, customBoard_print, customBoard_write
from strategy_data import strategies

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')  # Change this to DEBUG to see more info.

DISCOUNT_FACTOR = 1 #0.9

# cache the opponent's strategy
# TODO: Make this a function of the game state
STATE_VALUE_CACHE = {}
STATE_VISITED_CACHE = {}


def calculate(game, value_db, to_play):
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
            new_value = calculate(new_game, value_db, (to_play + 1) % 2) * prob
        else:
            new_value = calculate(new_game, value_db, to_play) * prob
        tot_value += new_value
        value_db[player_board + opponent_board][action] = (new_value, prob)
    return tot_value
    

def calc_counter_strategy(game_state, to_play, depth) -> float:
    '''
    Calculate the counter strategy for the given game state. The counter
    strategy is the best possible move for the opponent given that the
    player is playing the given strategy.
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
                value = -1 # value is 0 for player win
            else:
                next_to_play = (to_play + 1) % 2 if not collusion else to_play
                value = calc_counter_strategy(new_game, next_to_play, depth + 1)
            total_value += value * prob
        return total_value * (DISCOUNT_FACTOR ** depth)

    # opponent's turn
    # Check if we have already calculated the value of this state
    boards_combined = opponent_board + player_board
    if boards_combined in STATE_VISITED_CACHE:
        mx_value = -1
        for value_pair in STATE_VALUE_CACHE[opponent_board]:
            if value_pair[0] > mx_value:
                mx_value = value_pair[0]
        return mx_value * (DISCOUNT_FACTOR ** depth)

    # If we haven't calculated the value of this state, calculate it
    STATE_VISITED_CACHE[boards_combined] = True
    mx_value = -1 # maximum value initialized to -1
    possible_moves = [i for i, x in enumerate(opponent_board) if x == pieces.kEmpty]
    moves_considered = 0

    # for every possible move, calculate the probability of winning
    for action in possible_moves:
        new_game, collusion = play_action(game_state, opponent, action)
        if new_game in [pieces.kBlackWin, pieces.kWhiteWin]:
            value = 1 # value is 1 for opponent win
        else:
            next_to_play = (to_play + 1) % 2 if not collusion else to_play
            value = calc_counter_strategy(new_game, next_to_play, depth + 1)
        # update the cache
        if opponent_board in STATE_VALUE_CACHE:
            c = STATE_VALUE_CACHE[opponent_board][action]
            # update the value using the moving average
            STATE_VALUE_CACHE[opponent_board][action] = ((c[0] * c[1] + value) 
                                                            / (c[1] + 1), c[1] + 1)
        else:
            STATE_VALUE_CACHE[opponent_board][action] = (value, 1)
        # update the maximum value and the action
        if value > mx_value:
            mx_value = value
            total_value = value
            moves_considered = 1
        elif value == mx_value:
            total_value += value
            moves_considered += 1
    if moves_considered == 0:
        return total_value * (DISCOUNT_FACTOR ** depth)
    return (total_value / moves_considered) * (DISCOUNT_FACTOR ** depth)


def main():
    # initialize the log
    start = perf_counter()
    log.info('Timer started')
    
    # and let the user choose one
    game, file_name = choose_strategy()
    game_state = get_game_state(game)

    # Initialize the value database
    global STATE_VALUE_CACHE
    STATE_VALUE_CACHE = DefaultDict(lambda: [(0.0, 0) for i in range(12)])
    
    start = perf_counter()
    log.info('Timer started')

    turn = calculate_turn(game_state)

    # Save opponent moves to file - opp_info
    calc_counter_strategy(game_state, turn, 0)
    opp_strategy = greedify(STATE_VALUE_CACHE)
    # print(opp_strategy)
    # exit()
    game_state['opponent_strategy'] = opp_strategy

    # check if the file exists already;
    value_db = defaultdict(lambda: {})
    log.debug('Value database initialized')
    log.info('Calculating values for opponent strategy')
    opp_win_prob = calculate(game_state, value_db, turn)

    log.debug('Writing value database to file...')
    save_file(value_db, f'Data/{file_name}/value_db.pkl')
    
    log.debug('Writing opponent full strategy to file...')
    with open(f'Data/{file_name}/opp_strategy_text.txt', 'w') as f:
        for key, value in STATE_VALUE_CACHE.items():
            flag = False
            for i, (val, _count) in enumerate(value):
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

    # Save the opponent moves to file - opp_info
    save_file(opp_strategy, f'Data/{file_name}/opp_strategy.pkl')

if __name__ == '__main__':
    main()
    