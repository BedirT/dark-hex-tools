'''
Visually presents the game and probabilities after results of run.py.
Uses opp_info.pkl and info_states corresponding to the game.

Presents a possibility for the examiner to select a state to examine.
'''
import sys

from humanfriendly import text
sys.path.append('../../')

import logging
import coloredlogs
import pydot

from Projects.base.game.hex import pieces
from Projects.SVerify.util import calculate_turn, choose_strategy, conv_alphapos, game_over, get_game_state, load_file, play_action, save_file

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')  # Change this to DEBUG to see more info.


def gen_tree(tree, game_state, parent, depth, turn):
    '''
    Generates a pydot tree using players and opponents strategies.
    Each node is a move, and each edge is the probability of playing that move.
    'x's moves are black, 'o's moves are red.
    '''
    # Depending on the turn, choose the player or opponent strategy
    if turn == game_state['player_order']:
        strategy = game_state['player_strategy']
        to_play = game_state['player']
        board_to_play = game_state['boards'][game_state['player']]
    else:
        strategy = game_state['opponent_strategy']
        to_play = game_state['opponent']
        board_to_play = game_state['boards'][game_state['opponent']]

    # Add the child moves to the string with their probabilities
    for action, prob in strategy[board_to_play]:
        # Create the node
        alpha_action = conv_alphapos(action, game_state['num_cols'])
        id_str = f'{to_play}_{alpha_action}_{depth}'
        node = pydot.Node(id_str, label=f'{alpha_action}', shape='hexagon', 
                            color='black' if to_play == 'x' else 'red', style='filled',
                            fontcolor='white')
        tree.add_node(node)
        
        edge = pydot.Edge(parent, id_str, label=f'{prob:.2f}', color='black')
        tree.add_edge(edge)

        # Continue to the child of this move
        new_game_state, collusion = play_action(game_state, to_play, action)
        if new_game_state in [pieces.kBlackWin, pieces.kWhiteWin]:
            # If the game is over add an end node
            return tree
        tree = gen_tree(tree, new_game_state, id_str, depth+1, turn if collusion else (turn + 1) % 2)
    
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
    tree = pydot.Dot('my_graph', graph_type='digraph', bgcolor='white')
    
    # Add the root node
    root = pydot.Node('root', label='root', shape='circle')
    tree.add_node(root)

    # Add the tree
    tree = gen_tree(tree, game_state, 'root', 0, game_turn)

    # Save the tree dot file
    output_raw_dot = tree.to_string()
    save_file(output_raw_dot, f'Data/{file_name}/tree.dot')

  
if __name__ == '__main__':
    main()