"""
Visually presents the game and probabilities after results of run.py.
Uses opp_info.pkl and info_states corresponding to the game.

Presents a possibility for the examiner to select a state to examine.
"""
import copy
from copy import deepcopy

import pydot
import pyspiel
from darkhex.utils.util import (
    conv_alphapos,
    convert_os_strategy,
    get_open_spiel_state,
    load_file,
    save_file,
)


class TreeGenerator:

    def __init__(self, game, file_path):
        self.file_path = file_path

        # Load the game information
        self.game_info = load_file(
            f"{self.file_path}/game_info.pkl")
        self.player = self.game_info["player"]

        self.nc = 3
        self.nr = 3

        self.strat_color = 'black' if self.player == 0 else 'red'
        self.br_color = 'black' if self.player == 1 else 'red'

        self.strategies = {
            self.player:
                self.game_info["strategy"],
            1 - self.player:
                load_file(f"{self.file_path}/br_strategy.pkl"),
        }

        # Match game state to initial_state in game_info
        self.game_state = get_open_spiel_state(game,
                                               self.game_info["initial_board"])

        # tree componenets attributes
        self.attributes = {
            0: {
                "shape": "circle",
                "style": "filled",
                "fillcolor": "black",
                "fontname": "Monospace",
                "fontcolor": "white",
                "fontsize": "12",
                "width": "1.5",
                "height": "1.5",
            },
            1: {
                "shape": "circle",
                "style": "filled",
                "fillcolor": "red",
                "fontname": "Monospace",
                "fontsize": "12",
                "fontcolor": "white",
                "width": "1.5",
                "height": "1.5",
            },
            "edge": {
                "fontname": "Monospace",
                "fontsize": "12",
                "fontcolor": "black"
            },
            "0-terminal": {
                "shape": "doublecircle",
                "style": "filled",
                "fillcolor": "white",
                "fontname": "Monospace",
                "fontsize": "12",
                "fontcolor": "black",
            },
            "1-terminal": {
                "shape": "doublecircle",
                "style": "filled",
                "fillcolor": "black",
                "fontname": "Monospace",
                "fontsize": "12",
                "fontcolor": "white",
            },
            "-1-terminal": {
                "shape": "doublecircle",
                "style": "filled",
                "fillcolor": "red",
                "fontname": "Monospace",
                "fontsize": "12",
                "fontcolor": "white",
                "peripheries": "2",
                "linecolor": "black",
            },
            "root": {
                "shape": "circle",
                "style": "filled",
                "fillcolor": "darkgrey",
                "fontname": "Monospace",
                "fontsize": "12",
                "fontcolor": "white",
                "width": "1.5",
                "height": "1.5",
            },
        }

        # Create the tree
        self.generate_tree()

        # Save the tree
        self.save_tree_data()

    def generate_tree(self):
        # Start the tree
        self.tree_name = f"Strategy_Tree"
        self.tree = pydot.Dot(
            self.tree_name,
            graph_type="digraph",
            bgcolor="white",
            fontname="Monospace",
            fontsize="12",
            fontcolor="black",
            rankdir="TB",
            ratio="fill",
            size="8.3,11.7!",
            margin=0,
        )
        # Add the root node's children
        self._add_children(self.game_state)

    def save_tree_data(self):
        # Save the tree dot file
        output_raw_dot = self.tree.to_string()
        idx = output_raw_dot.find(self.tree_name + " {")
        legend_string = """\nsubgraph cluster_01 { 
            label = "Legend";
            style = "filled";
            color = "lightgrey";
            node [style=filled,color=white];
            a0 [label="Strat_P", color=%s, style=filled, fontcolor=white];
            a1 [label="BR_P", color=%s, style=filled, fontcolor=white];
        }""" % (self.strat_color, self.br_color)
        # add the legend to the dotcode
        output_raw_dot = (output_raw_dot[:idx + len(self.tree_name) + 2] +
                          legend_string +
                          output_raw_dot[idx + len(self.tree_name) + 2:])

        # Save the dot file
        save_file(output_raw_dot, f"{self.file_path}/tree.dot")

        # Save the tree
        self.tree.write_svg(f"{self.file_path}/tree.svg")
        self.tree.write_pdf(f"{self.file_path}/tree.pdf")

    def _add_children(self, game_state, parent=None):
        """
        Generates the children of the parent node.
        """
        info_state_0 = game_state.information_state_string(0)
        info_state_1 = game_state.information_state_string(1)
        info_state = game_state.information_state_string()
        cur_player = game_state.current_player()
        cur_player_terminal = 0 if cur_player == 0 else 1
        num_cols = self.nc

        if parent is None:
            # Add the root node
            info_state_str = self.tree_info_string(info_state_0, info_state_1)
            node_label = f"{info_state_str}"
            node = pydot.Node(node_label, **self.attributes["root"])
            self.tree.add_node(node)
            parent = node

        # Add an edge for each action
        for action, prob in self.strategies[cur_player][info_state]:
            # Update the game state
            new_game_state = game_state.child(action)

            # If terminal add terminal node
            if new_game_state.is_terminal():
                # Add node
                info_state_str = self.tree_info_string(
                    new_game_state.information_state_string(0),
                    new_game_state.information_state_string(1),
                )
                res = int(new_game_state.returns()[0])
                atr_label = f"{res}-terminal"
                terminal_node = pydot.Node(f"{info_state_str}", **self.attributes[atr_label])
                self.tree.add_node(terminal_node)

                # Add the edge if it doesnt already exist
                edge_label = f"{conv_alphapos(action, num_cols)}: {prob:.4f}"
                if not self.tree.get_edge(parent, terminal_node):
                    edge = pydot.Edge(
                        parent,
                        terminal_node,
                        label=edge_label,
                        **self.attributes["edge"],
                    )
                    self.tree.add_edge(edge)
            else:
                info_state_str = self.tree_info_string(
                    new_game_state.information_state_string(0),
                    new_game_state.information_state_string(1),
                )

                # Add the child node
                node_label = f"{info_state_str}"
                node = pydot.Node(node_label, **self.attributes[new_game_state.current_player()])
                self.tree.add_node(node)

                # Add the edge if it doesnt already exist
                edge_label = f"{conv_alphapos(action, num_cols)}: {prob:.4f}"
                if not self.tree.get_edge(parent, node):
                    edge = pydot.Edge(parent,
                                      node,
                                      label=edge_label,
                                      **self.attributes["edge"])
                    self.tree.add_edge(edge)

                # Add the child's children
                self._add_children(new_game_state, node)

    def tree_info_string(self, info_state_0, info_state_1):
        """ Converts the info_state to a string. TIC-TAC-TOE """
        s = ' p0|p1 \n---+---\n'
        is0 = info_state_0[3:].split('\n')
        is1 = info_state_1[3:].split('\n')
        for i, j in zip(is0, is1):
            s += i + '|' + j + '\n'
        return s