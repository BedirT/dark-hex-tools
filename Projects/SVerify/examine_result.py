'''
Visually presents the game and probabilities after results of run.py.
Uses opp_info.pkl and info_states corresponding to the game.

Presents a possibility for the examiner to select a state to examine.
'''
import pickle

from humanfriendly.terminal import ANSI_SHOW_CURSOR
from Projects.SVerify.run import calculate_turn, play_action
from strategy_data import strategies
from Projects.base.game.hex import pieces, multiBoard_print
import logging

import coloredlogs

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')  # Change this to DEBUG to see more info.

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
            i += 1; arr.append(strategy)
    choice = int(input('Enter your choice: '))
    return arr[choice]

def display_options(game_state, turn):
    '''
    Displays the moves and probabilities that were chosen.
    
    turn: 0 for player, 1 for opponent
    '''
    log.debug('Displaying options for turn: {}'.format(turn))
    log.debug('Board State: {}'.format(game_state['board']))
    if turn == game_state['player_order']:
        opts = game_state['player_strategy'][game_state['boards'][game_state['player']]]
        for i, (a, p) in enumerate(opts):
            print('{}. {} - {}'.format(i, a, p))
    else:
        try:
            opts = game_state['opponent_strategy'][game_state['boards'][game_state['opponent']]]
        except KeyError:
            log.critical('Opponent strategy missing board state: {}'.format(game_state['boards'][game_state['opponent']]))
            exit()
        if opts == -1:
            # Opponent loses no matter what
            print('Opponent loses no matter what')
            return -1, -1
        try:
            assert len(opts) > 0
        except AssertionError:
            log.critical('Opponent strategy is empty for board state: {}'.format(game_state['boards'][game_state['opponent']]))
            exit()
        for i, (a, p) in enumerate(opts):
            print('{}. {} - {}'.format(i, a, p))
    choice = int(input('Enter your choice: '))
    return opts[choice] if turn == game_state['player_order'] else opts[choice]

def main():
    opp_strategy = pickle.load(open('opp_info.pkl', 'rb'))
    game = choose_strategy()
    # set up the game
    game_state = {
        'board': game['board']
            if 'board' in game 
            else pieces.kEmpty * (game['num_rows'] * game['num_cols']),
        'boards': {
            game['player']: 
                game['boards'][game['player']]
                if 'boards' in game
                else pieces.kEmpty * (game['num_rows'] * game['num_cols']),
            pieces.kWhite if game['player'] == pieces.kBlack else pieces.kBlack: 
                game['boards'][pieces.kWhite if game['player'] == pieces.kBlack else pieces.kBlack]
                if 'boards' in game
                else pieces.kEmpty * (game['num_rows'] * game['num_cols'])
        },
        'num_rows': game['num_rows'],
        'num_cols': game['num_cols'],
        'first_player': game['first_player'],
        'player_order': game['player_order'],
        'player': game['player'],
        'opponent': pieces.kWhite if game['player'] == pieces.kBlack else pieces.kBlack,
        'player_strategy': game['strategy'],
        'opponent_strategy': opp_strategy
    }
    
    win_prob = 1
    game_turn = calculate_turn(game_state)
    log.debug('Game turn: {}'.format(game_turn))
    
    while(True):
        # play the game and examine from the beginning
        multiBoard_print(game_state['boards'][game_state['player']], game_state['boards'][game_state['opponent']], 
                         game_state['num_rows'], game_state['num_cols'], 
                         f'Player - {game_state["player"]}', f'Opponent - {game_state["opponent"]}')
        p_turn = game_state['player'] if game_turn == game_state['player_order'] else game_state['opponent']
        
        print(f'It is {p_turn}\'s turn, below are the moves that were examined for lower bound. \n' +
              'Please choose a move to proceed:')
        
        # display the moves and probabilities they were chosen
        action, prob = display_options(game_state, game_turn)
        
        # get the next state & display the current win probability in the branch
        game_state, end = play_action(game_state, p_turn, action)
        # print('The win probability for this branch is: {}'.format( ))
        if not end:
            # break
            game_turn = (game_turn + 1) % 2
    
if __name__ == '__main__':
    main()