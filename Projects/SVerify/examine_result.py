'''
Visually presents the game and probabilities after results of run.py.
Uses opp_info.pkl and info_states corresponding to the game.

Presents a possibility for the examiner to select a state to examine.
'''
from collections import defaultdict
import pickle
import dill
import logging
import coloredlogs
import sys
import os
from Projects.SVerify.util import calculate_turn, choose_strategy, conv_alphapos, get_game_state, load_file, play_action
sys.path.append('../../')

from Projects.base.game.hex import pieces, multiBoard_print, customBoard_print

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')  # Change this to DEBUG to see more info.
game_history = []


def display_options(game_state, win_probs, turn):
    '''
    Displays the moves and probabilities that were chosen.
    
    turn: 0 for player, 1 for opponent
    '''
    log.debug('Displaying options for turn: {}'.format(turn))
    log.debug('Board State: {}'.format(game_state['board']))
    
    # Add a rewind option if there is history
    if len(game_history) > 0:
        print('0. Rewind')

    w_probs = win_probs[game_state['boards'][game_state['player']] + game_state['boards'][game_state['opponent']]]
    
    if turn == game_state['player_order']:
        opts = game_state['player_strategy'][game_state['boards'][game_state['player']]]
        for i, (a, p) in enumerate(opts):
            val = w_probs[a][0] * w_probs[a][1]
            print('{}. {}({}) - {}: <{} wins:{:.2f} | {} wins:{:.2f}>'
                    .format(i+1, a, conv_alphapos(a, game_state['num_cols']), 
                            p, game_state['player'], val, game_state['opponent'], 1-val))
    else:
        try:
            opts = game_state['opponent_strategy'][game_state['boards'][game_state['opponent']]]
        except KeyError:
            log.critical('Opponent strategy missing board state: {}'.format(game_state['boards'][game_state['opponent']]))
            exit()
        if opts == -1:
            # Opponent loses no matter what
            print('Opponent loses no matter what')
            return -1, -1 # THIS IS WRONG FIX IT: -1 -1 is rewind
        try:
            assert len(opts) > 0
        except AssertionError:
            log.critical('Opponent strategy is empty for board state: {}'.format(game_state['boards'][game_state['opponent']]))
            exit()
        for i, (a, p) in enumerate(opts):
            val = w_probs[a][0] * w_probs[a][1]
            print('{}. {}({}) - {}: <{} wins:{:.2f} | {} wins:{:.2f}>'
                    .format(i+1, a, conv_alphapos(a, game_state['num_cols']), 
                            p, game_state['player'], val, game_state['opponent'], 1-val))

    # make sure the choice is valid
    try:
        choice = int(input('Enter your choice: '))
        if choice < 0 or choice > len(opts) or \
           (choice == 0 and len(game_history) == 0):
            raise ValueError
    except ValueError:
        print('Invalid choice')
        return display_options(game_state, win_probs, turn)
    return opts[choice-1] if choice != 0 else (-1, -1)


def end_game_choice(game, opp_strategy):
    # The game is over give the option to go back to the beginning
    # rewind a move or quit
    print('The game is over, please choose an option:')
    print('1. Go back to the beginning')
    print('2. Rewind a move')
    print('3. Quit')

    # make sure the choice is valid
    try:
        choice = int(input('Enter your choice: '))
        if choice < 1 or choice > 3:
            raise ValueError
    except ValueError:
        print('Invalid choice')
        return end_game_choice()
    if choice == 1:
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
        game_turn = calculate_turn(game_state)
    elif choice == 2:
        log.debug('Rewinding game')
        game_state = game_history.pop()
        game_turn = calculate_turn(game_state)
    elif choice == 3:
        return None, None
    return game_state, game_turn


def main():
    # load pickle file from SVerify/Data/FILE_NAME/opp_info.pkl
    game, file_name = choose_strategy()
    opp_strategy = load_file(f'Data/{file_name}/opp_info.pkl')
    # set up the game
    game_state = get_game_state(game, opp_strategy)
    game_turn = calculate_turn(game_state)
    log.debug('Loading win probabilities')
    value_db = load_file(f'Data/{file_name}/value_db.pkl')
    
    
    # Check the size of value db
    log.debug('Value DB type: {}'.format(type(value_db)))
    log.debug('Value DB size: {}'.format(len(value_db)))
    
    
    while(True):
        # play the game and examine from the beginning
        multiBoard_print(game_state['boards'][game_state['player']], 
                         game_state['boards'][game_state['opponent']], 
                         game_state['num_rows'], game_state['num_cols'], 
                         f'Player - {game_state["player"]}', f'Opponent - {game_state["opponent"]}')
        p_turn = game_state['player'] if game_turn == game_state['player_order'] else game_state['opponent']
        
        print(f'It is {p_turn}\'s turn, below are the moves that were examined for lower bound. \n' +
              'Please choose a move to proceed:')
        
        # display the moves and probabilities they were chosen
        action, prob = display_options(game_state, value_db, game_turn)

        # rewind the game
        if action == -1:
            log.debug('Rewinding game')
            game_state = game_history.pop()
            game_turn = calculate_turn(game_state)
            continue

        # save the game to rewind if the user wants to
        game_history.append(game_state)
        
        # get the next state & display the current win probability in the branch
        game_state, collusion = play_action(game_state, p_turn, action)
        # print('The win probability for this branch is: {}'.format( ))
        if not collusion:
            game_turn = (game_turn + 1) % 2
        if game_state in [pieces.kBlackWin, pieces.kWhiteWin]:
            game_state, game_turn = end_game_choice(game, opp_strategy)
            if game_state == None:
                break
  
  
if __name__ == '__main__':
    main()