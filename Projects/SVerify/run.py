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
from collections import defaultdict
from typing import DefaultDict
from copy import deepcopy
from time import perf_counter
import pickle
import logging
import coloredlogs
import sys
import os

import dill
from Projects.SVerify.util import calculate_turn, play_action
sys.path.append('../../')

from Projects.base.game.hex import pieces, customBoard_print, customBoard_write
from strategy_data import strategies

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')  # Change this to DEBUG to see more info.

discount_factor = 1 #0.9

# cache the opponent's strategy
# TODO: Make this a function of the game state
opp_state_value_cache = DefaultDict(lambda: [(0.0, 0) for i in range(12)]) # 3 x 4 = 12
opp_state_visited_cache = {}

def save_opp_info(info, file_name):
    '''
    Saves opp_info to a file to load it later. 
    Saves to SVerify/Data/FILE_NAME/opp_info.pkl
    '''
    log.info(f'Saving opponent strategy to folder: Data/{file_name}')
    with open(f'Data/{file_name}/opp_info.pkl', 'wb') as f:
        pickle.dump(info, f, pickle.HIGHEST_PROTOCOL)


def calculate(game, value_db, to_play):
    '''
    Given the player and opponent strategies. Calculate the lower bound.
    '''
    player_board = game['boards'][game['player']]
    opponent_board = game['boards'][game['opponent']]
    if opponent_board == 'x..xoox.....':
        print('Here')
    # whose turn
    if to_play == game['player_order']:
        # player's turn
        next_to_act = 'player'
        board_to_play = player_board
        strategy = game['strategy']
    else:
        # opponent's turn
        next_to_act = 'opponent'
        board_to_play = opponent_board
        strategy = game['opp_strategy']
    tot_value = 0
    # for every possible move, calculate the probability of winning
    for action, prob in strategy[board_to_play]:
        new_game, collusion = play_action(game, game[next_to_act], action)
        if new_game in [pieces.kBlackWin, pieces.kWhiteWin]:
            assert new_game == (pieces.kBlackWin if game[next_to_act] == pieces.kBlack else pieces.kWhiteWin)
            new_value = (0 if next_to_act == 'player' else 1) * prob
        elif not collusion:
            new_value = calculate(new_game, value_db, (to_play + 1) % 2) * prob
        else:
            new_value = calculate(new_game, value_db, to_play) * prob
        tot_value += new_value
        value_db[player_board + opponent_board][action] = (new_value, prob)
    return tot_value
        
def choose_strategy():
    '''
    User is displayed all the options in strategies
    and will pick one to run the algorithm for.
    '''
    print('Choose a strategy to run the algorithm for:')
    i = 0
    arr = []
    for name, strategy in vars(strategies).items():
        # no private variables
        if not name.startswith('__'):
            print('{}. {}'.format(i, name))
            i += 1; arr.append((strategy, name))
    # make sure the user picks a valid option
    try:
        choice = int(input('Enter your choice: '))
        if choice < 0 or choice >= len(arr):
            raise ValueError
    except ValueError:
        log.critical('Invalid choice...')
        return choose_strategy()
    return arr[choice][0], arr[choice][1]

def calc_opponent_strategy(game_state, to_play, depth):
    '''
    Plays the game using player strategy, and calculates the values for
    the opponent for every state possible. The values are stored in the
    cache, and used to generate the opponent strategy later on.
    
    A recursive implementation.
    '''
    player = game_state['player']
    opponent = game_state['opponent']
    player_order = game_state['player_order']
    opponent_board = game_state['boards'][opponent]
    player_board = game_state['boards'][player]
        
    total_value = 0
    if to_play == player_order:
        # player's turn
        strategy = game_state['strategy']
        for action, prob in strategy[player_board]:
            new_game, collusion = play_action(game_state, player, action)
            if new_game in [pieces.kBlackWin, pieces.kWhiteWin]:
                value = 0 # value is 0 for player win
            else:
                next_to_play = (to_play + 1) % 2 if not collusion else to_play
                value = calc_opponent_strategy(new_game, next_to_play, depth + 1)
            total_value += value * prob
        return total_value * (discount_factor ** depth)
    else:
        # opponent's turn
        boards_combined = opponent_board + player_board
        if boards_combined in opp_state_visited_cache:
            mx_value = -1
            for value_pair in opp_state_value_cache[opponent_board]:
                if value_pair[0] > mx_value:
                    mx_value = value_pair[0]
            total_value = mx_value
            return total_value * (discount_factor ** depth)
        else:
            opp_state_visited_cache[boards_combined] = True
        mx_value = -1 # maximum value
        possible_moves = [i for i, x in enumerate(opponent_board) if x == pieces.kEmpty]
        moves_considered = 0
        for action in possible_moves:
            new_game, collusion = play_action(game_state, opponent, action)
            if new_game in [pieces.kBlackWin, pieces.kWhiteWin]:
                # if the game is an instant win, player should
                # choose this move with probability 1
                value = 1 # value is 1 for opponent win
            else:
                next_to_play = (to_play + 1) % 2 if not collusion else to_play
                value = calc_opponent_strategy(new_game, next_to_play, depth + 1)
            # update the cache
            if opponent_board in opp_state_value_cache:
                c = opp_state_value_cache[opponent_board][action]
                # update the value using the moving average
                opp_state_value_cache[opponent_board][action] = ((c[0] * c[1] + value) / (c[1] + 1), c[1] + 1)
            else:
                opp_state_value_cache[opponent_board][action] = (value, 1)
            # update the maximum value and the action
            if value > mx_value:
                mx_value = value
                total_value = value
                moves_considered = 1
            elif value == mx_value:
                total_value += value
                moves_considered += 1
        if moves_considered == 0:
            return total_value * (discount_factor ** depth)
        return (total_value / moves_considered) * (discount_factor ** depth)

def greedify():
    strategy = {}
    for board_state, item in opp_state_value_cache.items():
        mx_value = 0
        actions = []
        valid_moves = [i for i, x in enumerate(board_state) if x == pieces.kEmpty]
        for idx, value_pair in enumerate(item):
            if idx not in valid_moves:
                continue
            if value_pair[0] > mx_value:
                mx_value = value_pair[0]
                actions = [idx]
            elif value_pair[0] == mx_value:
                actions.append(idx)
        strategy[board_state] = [(actions[i], 1 / len(actions)) for i in range(len(actions))]
    # print the strategy
    # for board_state, item in strategy.items():
    #     print('{} -> {}'.format(board_state, item))
    # exit()
    return strategy

def main():
    # initialize the log
    start = perf_counter()
    log.info('Timer started')
    # list all the strategies from strategies, display 
    # and let the user choose one
    strategy_dict, file_name = choose_strategy()
    game_state = {
        # use variable name as file_name
        'file_name': file_name,
        'num_rows': strategy_dict['num_rows'],
        'num_cols': strategy_dict['num_cols'],
        'player_order': strategy_dict['player_order'], # 0 or 1 depending on if player goes first
        'player': strategy_dict['player'], # player to evaluate - kBlack or kWhite
        'first_player': strategy_dict['first_player'], # kBlack or kWhite
        'opponent': pieces.kWhite if strategy_dict['player'] == pieces.kBlack else pieces.kBlack,
        'strategy': strategy_dict['strategy'],
        'board': strategy_dict['board']
            if 'board' in strategy_dict 
            else pieces.kEmpty * (strategy_dict['num_rows'] * strategy_dict['num_cols']),
        'boards': {
            strategy_dict['player']: 
                strategy_dict['boards'][strategy_dict['player']]
                if 'boards' in strategy_dict
                else pieces.kEmpty * (strategy_dict['num_rows'] * strategy_dict['num_cols']),
            pieces.kWhite if strategy_dict['player'] == pieces.kBlack else pieces.kBlack: 
                strategy_dict['boards'][pieces.kWhite if strategy_dict['player'] == pieces.kBlack else pieces.kBlack]
                if 'boards' in strategy_dict
                else pieces.kEmpty * (strategy_dict['num_rows'] * strategy_dict['num_cols'])
        },
    }
    FILE_NAME = game_state['file_name']
    log.info('Game state initialized')
    start = perf_counter()
    log.info('Timer started')
    turn = calculate_turn(game_state)
    
    # Save opponent moves to file - opp_info
    calc_opponent_strategy(game_state, turn, 0)
    
    # Greedy policy/strategy for opponent
    opp_strategy = greedify()
    game_state['opp_strategy'] = opp_strategy
    
    # check if the file exists already;
    value_db = defaultdict(lambda: dict())
    log.debug('Value database initialized')
    log.debug('Calculating value database')
    opp_win_prob = calculate(game_state, value_db, turn)
    # save win_probs to pickle file with name: Data/FILE_NAME/win_probs.pkl
    # create file if it doesn't exist
    if not os.path.exists('Data/{}'.format(FILE_NAME)):
        os.makedirs('Data/{}'.format(FILE_NAME))
    dill.dump(value_db, open('Data/{}/value_db.pkl'.format(FILE_NAME), 'wb'))
    # Play the game and report the win probability of the player
    
    # print the win probability with the boards to file
    # file is saved in SVerify/Data/FILE_NAME/opp_strat_full.txt
    log.debug('Writing opponent full strategy to file')
    # Create the directory if it does not exist Data/FILE_NAME
    if not os.path.exists('Data/' + FILE_NAME):
        os.makedirs('Data/' + FILE_NAME)
    with open('Data/' + FILE_NAME + '/opp_strat_full.txt', 'w') as f:
        for key, value in opp_state_value_cache.items():
            flag = False
            for i, (val, count) in enumerate(value):
                if val > 0:
                    if not flag:
                        customBoard_write(key, game_state['num_cols'], game_state['num_rows'], f)
                        f.write('Strategy for the board {}: \n'.format(key))
                        flag = True
                    f.write('{}: {}\n'.format(i, val))
            if flag:
                f.write('\n')
        
    # Report the win probability
    log.info('Win probability: {}'.format(1 - opp_win_prob))
    
    # Report the time taken
    log.info(f"Time took: {perf_counter() - start}")
    
    # Save the opponent moves to file - opp_info
    save_opp_info(opp_strategy, FILE_NAME)

if __name__ == '__main__':
    main()