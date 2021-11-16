'''
Visually presents the game and probabilities after results of run.py.
Uses opp_info.pkl and info_states corresponding to the game.

Presents a possibility for the examiner to select a state to examine.
'''
import pickle
from Projects.SVerify.run import play_action
from strategy_data import strategies
from Projects.base.game.hex import pieces, multiBoard_print

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

def display_options(boards, player_strategy, opp_strategy, p, turn):
    '''
    Displays the moves and probabilities that were chosen.
    
    turn: 0 for player, 1 for opponent
    '''
    if turn == 0:
        # print('Player\'s turn')
        opts = player_strategy[boards[p]]
        for i, (a, p) in enumerate(opts):
            print('{}. {} - {}'.format(i, a, p))
    else:
        opts = opp_strategy[boards[pieces.kBlack] + boards[pieces.kWhite]]
        for i, a in enumerate(opts):
            p = 1 / len(opts)
            print('{}. {} - {}'.format(i, a, p))
    choice = int(input('Enter your choice: '))
    if choice == -1:
        return None
    
    return opts[choice] if turn == 0 else (opts[choice], 1 / len(opts))

def main():
    opp_strategy = pickle.load(open('Projects/SVerify/opp_info2.pkl', 'rb'))
    game = choose_strategy()
    player_strategy = game['strategy']
    
    # set up the board
    num_rows = game['num_rows']
    num_cols = game['num_cols']
    
    player_color = game['player']
    opp_color = pieces.kWhite if game['player'] == pieces.kBlack else pieces.kBlack
    player_order = game['player_order']
    first_player = game['first_player']
    
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
        'num_rows': num_rows,
        'num_cols': num_cols,
    }
    
    cont = 0
    win_prob = 1
    
    while(True):
        # play the game and examine from the beginning
        multiBoard_print(game_state['boards'][player_color], game_state['boards'][opp_color], num_rows, num_cols, 'Player - '+player_color, 'Opponent - '+opp_color)
        p_turn = player_color if cont % 2 == player_order else opp_color 
        print(f'It is {p_turn}\'s turn, below are the moves that were examined for lower bound. \n' +
              'Please choose a move to proceed:')
        
        # display the moves and probabilities they were chosen
        action, prob = display_options(game_state['boards'], player_strategy, opp_strategy, player_color, 0 if p_turn == player_color else 1)
        print(action, prob)
        # get the next state & display the current win probability in the branch
        game_state, end = play_action(game_state, p_turn, action)
        # print('The win probability for this branch is: {}'.format( ))
        if end:
            break
        
        cont += 1
    
if __name__ == '__main__':
    main()