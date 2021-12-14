'''
Visually presents the game and probabilities after results of run.py.
Uses opp_info.pkl and info_states corresponding to the game.

Presents a possibility for the examiner to select a state to examine.
'''
import logging
import coloredlogs
import sys
from ete3 import Tree

from Projects.SVerify.util import calculate_turn, choose_strategy, conv_alphapos, game_over, get_game_state, load_file, play_action, save_file
sys.path.append('../../')

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')  # Change this to DEBUG to see more info.


def gen_newick_string(final_string, game_state, turn):
    '''
    Generates a newick string for the tree.
    '''
    # Setup the strategies
    player_strategy = game_state['player_strategy']
    opponent_strategy = game_state['opponent_strategy']
    
    # Setup the boards
    player_board = game_state['boards'][game_state['player']]
    opponent_board = game_state['boards'][game_state['opponent']]
    
    # Depending on the turn, choose the player or opponent strategy
    if turn == game_state['player_order']:
        strategy = player_strategy
        to_play = game_state['player']
    else:
        strategy = opponent_strategy
        to_play = game_state['opponent']
        
    # Add paranthases to the final string
    final_string += '('
        
    # Add the child moves to the string with their probabilities
    for action, prob in strategy[player_board]:
        final_string += '{}:{},'.format(action, prob)
        
        # Continue to the child of this move
        new_game_state, collusion = play_action(game_state, to_play, action)
        if game_over(new_game_state):
            return final_string[:-1] + ')'
        final_string = gen_newick_string(final_string, new_game_state, turn if collusion else (turn + 1) % 2)
        
    # Add paranthases to the final string
    final_string += ')'
    
    return final_string    
    
        
def gen_tree(newick_string):
    '''
    Generates the tree using ETE.
    '''
    tree = Tree(newick_string)
    tree.set_outgroup(tree.get_leaves()[0])
    return tree


def main():
    game, file_name = choose_strategy()
    
    # Load opponent strategy
    opp_strategy = load_file(f'Data/{file_name}/opp_info.pkl')
    
    # Set up the game
    game_state = get_game_state(game, opp_strategy)
    game_turn = calculate_turn(game_state)
    
    # Load win probabilities
    # log.debug('Loading win probabilities')
    # value_db = load_file(f'Data/{file_name}/value_db.pkl')
    
    # Call gen_tree to generate the tree
    newick_string = gen_newick_string(game_state, game_turn)
    
    # Generate the tree using ETE and newick string
    tree = gen_tree(newick_string)
    
    # Display the tree
    tree.show()
    
    # Save the tree to a file
    save_file(tree, f'Data/{file_name}/tree.pkl')
  
  
if __name__ == '__main__':
    main()