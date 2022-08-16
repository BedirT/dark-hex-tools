import copy
from copy import deepcopy

import pydot
import pyspiel
import darkhex.utils.util as util
import darkhex.policy as darkhexPolicy


class TreeGenerator:
    """
    Visually presents a game and probabilities for given policies for both players.
    """

    def __init__(self, policy_0: darkhexPolicy, policy_1: darkhexPolicy,
                 name_0: str, name_1: str):
        """
        Initializes the TreeGenerator.

        Args:
            policy_0 (darkhexPolicy): The policy for player 0.
            policy_1 (darkhexPolicy): The policy for player 1.
            name_0 (str): The name of player 0. Be descriptive as this will be used in the filename.
            name_1 (str): The name of player 1. Be descriptive as this will be used in the filename.
        """
        assert policy_0.board_size == policy_1.board_size, "Policies must be for the same board size"
        self.num_cols = policy_0.num_cols
        self.num_rows = policy_0.num_rows

        self.name_0 = name_0
        self.name_1 = name_1

        self.game = pyspiel.load_game(
            "dark_hex_ir", {
                "num_rows": self.num_rows,
                "num_cols": self.num_cols,
                "use_early_terminal": True
            })
        self.game_state = self.game.new_initial_state()

        self.policies = {
            0: policy_0,
            1: policy_1,
        }

        # tree componenets attributes
        self.attributes = {
            0: {
                "shape": "hexagon",
                "style": "filled",
                "fillcolor": "gray14",
                "fontname": "Monospace",
                "fontcolor": "ghostwhite",
                "fontsize": "12",
                "width": "1.5",
                "height": "1.5",
            },
            1: {
                "shape": "hexagon",
                "style": "filled",
                "fillcolor": "ghostwhite",
                "fontname": "Monospace",
                "fontsize": "12",
                "fontcolor": "gray14",
                "width": "1.5",
                "height": "1.5",
            },
            "edge": {
                "fontname": "Monospace",
                "fontsize": "12",
                "fontcolor": "gray14"
            },
            "0-terminal": {
                "shape": "doublecircle",
                "style": "filled",
                "fillcolor": "gray14",
                "fontname": "Monospace",
                "fontsize": "12",
                "fontcolor": "ghostwhite",
            },
            "1-terminal": {
                "shape": "doublecircle",
                "style": "filled",
                "fillcolor": "ghostwhite",
                "fontname": "Monospace",
                "fontsize": "12",
                "fontcolor": "gray14",
                "peripheries": "2",
                "linecolor": "gray14",
            },
            "root": {
                "shape": "hexagon",
                "style": "filled",
                "fillcolor": "snow3",
                "fontname": "Monospace",
                "fontsize": "12",
                "fontcolor": "gray14",
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
        self.tree_name = f"{self.name_0}_{self.name_1}"
        self.tree = pydot.Dot(
            self.tree_name,
            graph_type="digraph",
            bgcolor="mintcream",
            fontname="Monospace",
            fontsize="12",
            fontcolor="gray14",
            rankdir="TB",
            ratio="fill",
            size="8.3,11.7",
            margin=5,
        )
        # Add the root node's children
        self._add_children(self.game_state)

    def save_tree_data(self):
        # Save the tree dot file
        output_raw_dot = self.tree.to_string()
        path = f"{util.PathVars.game_trees}{self.name_0}-{self.name_1}"
        # Save the dot file
        util.save_file(output_raw_dot, f"{path}/tree.dot")

        # Save the tree
        self.tree.write_svg(f"{path}/tree.svg")
        self.tree.write_pdf(f"{path}/tree.pdf")

    def _add_children(self, game_state, parent=None):
        """
        Generates the children of the parent node.
        """
        info_state_0 = game_state.information_state_string(0)
        info_state_1 = game_state.information_state_string(1)
        info_state = game_state.information_state_string()
        cur_player = game_state.current_player()
        cur_player_terminal = 0 if cur_player == 0 else 1

        if parent is None:
            # Add the root node
            info_state_str = self.tree_info_string(info_state_0, info_state_1)
            node_label = f"{info_state_str}"
            node = pydot.Node(node_label, **self.attributes["root"])
            self.tree.add_node(node)
            parent = node

        # Add an edge for each action
        a_p = self.policies[cur_player].get_action_probabilities(
            info_state).items()
        for action, prob in a_p:
            # Update the game state
            new_game_state = game_state.child(action)

            # If terminal add terminal node
            if new_game_state.is_terminal():
                # Add node
                info_state_str = self.tree_info_string(
                    new_game_state.information_state_string(0),
                    new_game_state.information_state_string(1),
                )
                terminal_node = pydot.Node(
                    f"{info_state_str}",
                    **self.attributes[f"{cur_player_terminal}-terminal"],
                )
                self.tree.add_node(terminal_node)

                # Add the edge if it doesnt already exist
                edge_label = f"{util.convert_position_to_alphanumeric(action, self.num_cols)}: {prob:.4f}"
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
                node = pydot.Node(node_label, **self.attributes[cur_player])
                self.tree.add_node(node)

                # Add the edge if it doesnt already exist
                edge_label = f"{util.convert_position_to_alphanumeric(action, self.num_cols)}: {prob:.4f}"
                if not self.tree.get_edge(parent, node):
                    edge = pydot.Edge(parent,
                                      node,
                                      label=edge_label,
                                      **self.attributes["edge"])
                    self.tree.add_edge(edge)

                # Add the child's children
                self._add_children(new_game_state, node)

    def tree_info_string(self, info_state_0, info_state_1):
        """ Converts the info_state to a string. """
        info_str = ""
        line_num = 1
        line_str_0 = ""
        line_str_1 = ""
        for idx, (is_0_cell,
                  is_1_cell) in enumerate(zip(info_state_0, info_state_1)):
            # if beginning of a new line
            if idx % self.num_cols == 0 and idx != 0:
                # add the strings to the info_str
                # add \n and spaces amount of the row number
                info_str += f"\n{'':>{line_num-1}}{line_str_0}  {line_str_1}"
                line_num += 1
                line_str_0 = str(is_0_cell)
                line_str_1 = str(is_1_cell)
            else:
                # add the cell to the string
                line_str_0 += f"{is_0_cell}"
                line_str_1 += f"{is_1_cell}"
        # add the last line
        info_str += f"\n{'':>{line_num-1}}{line_str_0}  {line_str_1}"
        return info_str
