'''
Visually presents the game and probabilities after results of run.py.
Uses opp_info.pkl and info_states corresponding to the game.

Presents a possibility for the examiner to select a state to examine.
'''
from copy import deepcopy
import sys
sys.path.append('../../')

from Projects.SVerify.utils.util import conv_alphapos, convert_os_strategy, get_open_spiel_state
from Projects.SVerify.utils.util import load_file
from Projects.SVerify.utils.util import save_file

import logging
import coloredlogs
import pydot
import pyspiel

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')  # Change this to DEBUG to see more info.


class TreeGenerator:
    def __init__(self, game, file_name):
        self.file_name = file_name

        # Load the game information
        self.game_info = load_file(f'Data/strategy_data/{self.file_name}/game_info.pkl')

        # TODO: Remove after fixing the generate_info_states.py
        player = 0 if self.game_info['player'] == 'x' else 1 

        self.strategies = {
            player: convert_os_strategy(self.game_info['strategy'], self.game_info['num_cols'], player),
            1 - player: load_file(f'Data/strategy_data/{self.file_name}/opp_strategy.pkl')
        }

        # Match game state to initial_state in game_info
        self.game_state = get_open_spiel_state(game, self.game_info['initial_board'])

        # tree componenets attributes
        self.attributes = {
            0: {'shape': 'hexagon', 'style': 'filled', 'fillcolor': 'white',
                'fontname': 'Helvetica', 'fontsize': '12', 'fontcolor': 'black'},
            1: {'shape': 'hexagon', 'style': 'filled', 'fillcolor': 'white',
                'fontname': 'Helvetica', 'fontsize': '12', 'fontcolor': 'black'},
            'edge': {'fontname': 'Helvetica', 'fontsize': '12', 'fontcolor': 'black'},
            '0-terminal': {'shape': 'doublecircle', 'style': 'filled', 'fillcolor': 'black',
                            'fontname': 'Helvetica', 'fontsize': '12', 'fontcolor': 'white'},
            '1-terminal': {'shape': 'doublecircle', 'style': 'filled', 'fillcolor': 'white',
                            'fontname': 'Helvetica', 'fontsize': '12', 'fontcolor': 'black',
                            'peripheries': '2', 'linecolor': 'black'},
        }

        # Create the tree
        self.generate_tree()

        # Save the tree
        self.save_tree_data()

    def generate_tree(self):
        # Start the tree
        self.tree = pydot.Dot('Strategy Tree', graph_type='digraph', bgcolor='white',
                              fontname='Helvetica', fontsize='12', fontcolor='black',
                              rankdir='TB')

        # Add the root node
        self.root = pydot.Node(self.game_state.information_state_string(),
                               shape='circle', style='filled', fillcolor='white',
                               fontname='Helvetica', fontsize='12', fontcolor='black')
        self.tree.add_node(self.root)

        # Add the root node's children
        self._add_children(self.root, self.game_state)

    def save_tree_data(self):
        # Save the tree dot file
        output_raw_dot = self.tree.to_string()
        idx = output_raw_dot.find('my_graph {')
        legend_string = '''\nsubgraph cluster_01 { 
            label = "Legend";
            style = "filled";
            color = "lightgrey";
            node [style=filled,color=white];
            a0 [label="x", shape=hexagon, color=black, style=filled, fontcolor=white];
            a1 [label="o", shape=hexagon, color=white, style=filled, fontcolor=black, linecolor=black];
        }'''
        # add the legend to the dotcode
        output_raw_dot = output_raw_dot[:idx + len('my_graph {')] + \
                         legend_string + output_raw_dot[idx + len('my_graph {'):]

        # Save the dot file
        save_file(output_raw_dot, f'Data/strategy_data/{self.file_name}/tree.dot')

        # Save the tree
        # self.tree.write_png(f'Data/strategy_data/{self.file_name}/tree.pdf')

    def _add_children(self, parent, game_state):
        '''
        Generates the children of the parent node.
        '''
        info_state = game_state.information_state_string()
        cur_player = game_state.current_player()
        cur_player_str = '0' if cur_player == 0 else '1'
        # Create the node
        node_label = f'{info_state}'
        node = pydot.Node(node_label, **self.attributes[cur_player])
        self.tree.add_node(node)

        # Add an edge for each action
        for action, prob in self.strategies[cur_player][info_state]:
            num_cols = self.game_info['num_cols']
            edge_label = f'{conv_alphapos(action, num_cols)}: {prob:.2f}'
            edge = pydot.Edge(parent, node, label=edge_label, **self.attributes['edge'])

            self.tree.add_edge(edge)

            # Update the game state
            new_game_state = deepcopy(game_state)
            new_game_state.apply_action(action)   

            # If terminal add terminal node
            if new_game_state.is_terminal():
                terminal_node = pydot.Node('', **self.attributes[f'{cur_player_str}-terminal'])
                self.tree.add_node(terminal_node)
                edge = pydot.Edge(node, terminal_node, **self.attributes['edge'])
                self.tree.add_edge(edge) 
            else:
                # Add the child node
                self._add_children(node, new_game_state)
