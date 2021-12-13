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
sys.path.append('../../')

from run import calculate_turn, play_action
from strategy_data import strategies
from Projects.base.game.hex import pieces, multiBoard_print, customBoard_print

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')  # Change this to DEBUG to see more info.
game_history = []

CALC_WINS = True

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
    
    # make sure the choice is valid
    try:
        choice = int(input('Enter your choice: '))
        if choice < 0 or choice >= len(arr):
            raise ValueError
    except ValueError:
        print('Invalid choice')
        return choose_strategy()
    return arr[choice][0], arr[choice][1]

def conv_alphapos(pos, num_cols=8):
    '''
    Converts a position to a letter and number
    pos: int
    '''
    col = pos % num_cols
    row = pos // num_cols
    return '{}{}'.format(chr(ord('a') + col), row + 1)

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

    # multiBoard_print(game_state['boards'][game_state['player']], game_state['boards'][game_state['opponent']], 
    #                  game_state['num_rows'], game_state['num_cols'], 'Player', 'Opponent')
    # print(game_state['player_strategy'][game_state['boards'][game_state['player']]] \
    #         if turn == game_state['player_order'] 
    #         else game_state['opponent_strategy'][game_state['boards'][game_state['opponent']]])
    # print('Win Probabilities:{}'.format(w_probs))
    # input()
    
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
    opp_strategy = pickle.load(open('Data/{}/opp_info.pkl'.format(file_name), 'rb'))
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
    game_turn = calculate_turn(game_state)
    log.debug('Game turn: {}'.format(game_turn))

    win_probs = defaultdict(lambda: dict())
    if not os.path.isfile('Data/{}/value_db.pkl'.format(file_name)):
        # if not, calculate the win probabilities
        log.debug('Could not find win probabilities file, calculating')
        calculate_win_probs(game_state, win_probs, game_turn)
        # save win_probs to pickle file with name: Data/file_name/win_probs.pkl
        dill.dump(win_probs, open('Data/{}/value_db.pkl'.format(file_name), 'wb'))
    else:
        # if the file exists, load it
        log.debug('Loading win probabilities')
        win_probs = dill.load(open('Data/{}/value_db.pkl'.format(file_name), 'rb'))

    while(True):
        # play the game and examine from the beginning
        multiBoard_print(game_state['boards'][game_state['player']], game_state['boards'][game_state['opponent']], 
                         game_state['num_rows'], game_state['num_cols'], 
                         f'Player - {game_state["player"]}', f'Opponent - {game_state["opponent"]}')
        p_turn = game_state['player'] if game_turn == game_state['player_order'] else game_state['opponent']
        
        print(f'It is {p_turn}\'s turn, below are the moves that were examined for lower bound. \n' +
              'Please choose a move to proceed:')
        
        # display the moves and probabilities they were chosen
        action, prob = display_options(game_state, win_probs, game_turn)

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
  
def calculate_win_probs(game_state, win_probs, to_play):
    '''
    Plays the game and calculates the win probability for each move 
    for Black and White. Recursively calls itself to play the game
    until the game is over, then returns the win probability for the end
    game, multiplied by the probabilities as it goes back up the tree.
    Args:
        game_state: the current game state
        win_probs: the win probability dictionary. For each state it contains
            the win probability (for opponent) for each action.
    Returns:
        win_probs: the win probability for each move for opponent
    '''
    player_board = game_state['boards'][game_state['player']]
    opponent_board = game_state['boards'][game_state['opponent']]

    if player_board + opponent_board in win_probs:
        tot = 0
        for key, value in win_probs[player_board + opponent_board].items():
            tot += value[0] * value[1] # value * probability
        return tot

    # whose turn
    if to_play == game_state['player_order']:
        # player's turn
        next_to_act = 'player'
        board_to_play = player_board
        strategy = game_state['player_strategy']
    else:
        # opponent's turn
        next_to_act = 'opponent'
        board_to_play = opponent_board
        strategy = game_state['opponent_strategy']

    win_p = 0
    for action, prob in strategy[board_to_play]:
        # get the next state
        new_game, collusion = play_action(game_state, game_state[next_to_act], action)
        if new_game in [pieces.kBlackWin, pieces.kWhiteWin]:
            assert new_game == (pieces.kBlackWin if game_state[next_to_act] == pieces.kBlack else pieces.kWhiteWin)
            new_p = (0 if next_to_act == 'player' else 1) * prob
        elif not collusion:
            new_p = calculate_win_probs(new_game, win_probs, (to_play + 1) % 2) * prob
        else:
            new_p = calculate_win_probs(new_game, win_probs, to_play) * prob
        win_p += new_p
        win_probs[player_board + opponent_board][action] = (new_p, prob) # opp wins
    return win_p


if __name__ == '__main__':
    main()