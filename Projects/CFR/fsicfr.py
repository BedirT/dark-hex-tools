import numpy as np
from Projects.base.util.print_tools import seq_to_str
from Projects.base.game.darkHex import DarkHex
from Projects.base.game.hex import Hex
from tqdm import tqdm
from copy import deepcopy, copy
from Projects.base.util.colors import pieces
from collections import defaultdict
import pickle

class Node:
    def __init__(self, board, move_history, player, h) -> None:
        self.player = player
        self.num_actions = len(board)
        self.move_history = move_history
        self.board = deepcopy(board)
        self.h = h

        self.infoSet = get_infoset([self.player, *self.board, self.h])

        self.strategy = np.zeros(self.num_actions)
        self.regretSum = np.zeros(self.num_actions)
        self.strategySum = np.zeros(self.num_actions)
        self.regrets = np.zeros(self.num_actions)

        self.T = 0
        self.u = 0
        self.pSum1 = 1
        self.pSum2 = 1
        self.visits = 1

        self.pos_actions = [i for i, x in enumerate(self.board) if x == pieces.NEUTRAL]

        self.is_terminal = False

    def getStrategy(self): 
        normalizingSum = 0
        for a in self.pos_actions:
            self.strategy[a] = max(self.regretSum[a], 0)
            # * regret matching algorithm here.
            # * just use the positive regrets.
            normalizingSum += self.strategy[a]
            # Add all the positive regrets -> normSum
        for a in self.pos_actions:
            if normalizingSum > 0:
                # if normalizing sum was positive all the action probs will
                # be devided by normSum
                self.strategy[a] /= normalizingSum
            else:
                # otherwise all actions are equaprobable (random)
                self.strategy[a] = 1.0 / len(self.pos_actions)
            self.strategySum[a] += self.strategy[a] * (self.pSum1 if \
                    self.player == pieces.C_PLAYER1 else self.pSum2)
            # * summing up all the action probabilities
            # ? what is realizationWeight again
        return self.strategy

    def getAverageStrategy(self):
        normalizingSum = 0
        for a in self.pos_actions:
            normalizingSum += self.strategySum[a]
            # summing up all the action probs using strategySum
            # ? why strategySum
        for a in self.pos_actions:
            if normalizingSum > 0:
                self.strategySum[a] /= normalizingSum
            else:
                self.strategySum[a] = 1 / len(self.pos_actions)
        return self.strategySum

    def __str__(self):
        return "{}:\t{}".format(self.infoSet, seq_to_str(self.getAverageStrategy(), spacing=' '))


class FSICFR:
    def __init__(self, num_rows=3, num_cols=3) -> None:
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_actions = num_cols * num_rows
        self.nodes, self.nodes_dict = self.__init_board_topSorted()

    def train(self, num_of_iterations) -> None:
        for it in tqdm(range(num_of_iterations)):
            for node in self.nodes: # top-sorted nodes
                if node.visits == 0:
                    node.visits = 1
                    node.pSum1 = 1 
                    node.pSum2 = 1
                rev_player = pieces.C_PLAYER1 if node.player == pieces.C_PLAYER2 else pieces.C_PLAYER2
                strategy = node.getStrategy()
                for a in node.pos_actions: 
                    # for each possible move
                    # take action a on board
                    children = []
                    # * update the board with action a and add the new
                    # * board state to the -children- to traverse later
                    new_board = self.__add_stone(node.board, a, node.player)
                    children.append(get_infoset([node.player, *new_board, node.h]))
                    if node.h > 0:
                        new_board = self.__add_stone(node.board, a, rev_player)
                        children.append(get_infoset([node.player, *new_board, node.h-1]))
                    for infoset_c in children:
                        if infoset_c in self.nodes_dict:
                            # update visits
                            c = self.nodes_dict[infoset_c]
                            c.visits += node.visits
                            # update the rweights
                            c.pSum1 += (strategy[a] * node.pSum1 if node.player == pieces.C_PLAYER1 else node.pSum1)
                            c.pSum2 += (strategy[a] * node.pSum2 if node.player == pieces.C_PLAYER2 else node.pSum2)
                # endfor - pos_actions
            # endfor - nodes
            for node in self.nodes[::-1]:
                node.u = 0
                strategy = node.getStrategy()
                rev_player = pieces.C_PLAYER1 if node.player == pieces.C_PLAYER2 else pieces.C_PLAYER2
                game = Hex(BOARD_SIZE=[self.num_rows, self.num_cols],
                           BOARD=node.board, verbose=False)
                if game.game_status() == node.player:
                    node.u = 1
                elif game.game_status() != '=':
                    node.u = -1
                else:
                    for a in range(self.num_actions):
                        children = []
                        # * update the board with action a and add the new
                        # * board state to the -children- to traverse later
                        new_board = self.__add_stone(node.board, a, node.player)
                        if not new_board:
                            continue
                        children.append(get_infoset([node.player, *new_board, node.h]))
                        if node.h > 0:
                            new_board = self.__add_stone(node.board, a, rev_player)
                            if not new_board:
                                continue
                            children.append(get_infoset([node.player, *new_board, node.h-1]))
                        for _, infoset_c in enumerate(children):
                            if infoset_c in self.nodes_dict:
                                if self.nodes_dict[infoset_c].player == node.player:
                                    childUtil = self.nodes_dict[infoset_c].u
                                else:
                                    childUtil = - self.nodes_dict[infoset_c].u
                                node.regrets[a] += childUtil
                                node.u += strategy[a] * childUtil
                    cfp = node.pSum2 if node.player == pieces.C_PLAYER1 else node.pSum1
                    for a in node.pos_actions:
                        nomin = (node.T * node.regretSum[a] + node.visits * cfp * (node.regrets[a] - node.u))
                        denom = node.T + node.visits
                        node.regretSum[a] = nomin / denom
                    node.T += node.visits

                node.visits = 0
                node.pSum1 = 0 
                node.pSum2 = 0
            
            # reset the strategysums - page 32
            if it == num_of_iterations//2:
                for node in self.nodes:
                    for a in range(len(node.strategySum)):
                        node.strategySum[a] = 0

        for node in self.nodes:
            if not node.is_terminal:
                print(node.infoSet, node.getAverageStrategy())
                
    def __init_board_topSorted(self) -> list:
        # TODO: Remove more states using pONE
        stack = []; nodes_dict = {}; visited = defaultdict(lambda: False)
        game = DarkHex([self.num_rows, self.num_cols], False)
        self.__topSort_play(game, '=', stack, visited, nodes_dict)
        print("Phase 1 has ended...")
        print("{} number of unique states".format(len(nodes_dict)))
        return stack[-1::-1], nodes_dict

    def __topSort_play(self, game, res, stack, visited, nodes_dict) -> None:
        player = game.turn_info()
        # * Given a game, return the top-sorted full states 
        # -------------------------------------------------
        # -> Create the node for the current game&player
        # -> Player plays every possible action
        # -> Call the next game
        # -> Save the infoSet + node
        ext_infoSet = tuple([*game.BOARDS[game.C_PLAYER1], *game.BOARDS[game.C_PLAYER2]])
        if res == 'f':
            node = Node(board=game.BOARDS[player], 
                        move_history=game.move_history[player],
                        player=player, 
                        h=game.totalHidden_for_player(player))
            if visited[ext_infoSet]:
                return 
            else:
                visited[ext_infoSet] = True
        else:
            # * CREATING THE NODE *********
            if res != '=':
                player = res
            new_h = game.totalHidden_for_player(player)
            node = Node(board=game.BOARDS[player], 
                        move_history=game.move_history[player],
                        player=player, 
                        h=new_h)                     
            node.is_terminal = res != '='
            # *******************************
            if visited[ext_infoSet]:
                return
            else:
                visited[ext_infoSet] = True

        if node.is_terminal:
            if node.infoSet not in nodes_dict:
                nodes_dict[node.infoSet] = node
                stack.append(node)
            return
             
        valid_moves = copy(game.valid_moves_colors[player])
        for a in valid_moves:
            _, _, res, _ = game.step(player, a)
            self.__topSort_play(game, res, stack, visited, nodes_dict)
            game.rewind(res == 'f')
        if node.infoSet not in nodes_dict:
            nodes_dict[node.infoSet] = node
            stack.append(node)
        return

    def __add_stone(self, board, action, player):
        new_board = deepcopy(board)
        if new_board[action] != '.':
            return False
        new_board[action] = player
        return new_board


def get_infoset(args) -> tuple:
    return tuple([*args])

num_cols = 3
num_rows = 3

# UNCOMMENT - PHASE 1
cfr = FSICFR(num_cols=num_cols, num_rows=num_rows)

with open('ph1-cfr-{}x{}.pkl'.format(num_cols, num_rows), 'wb') as f:
    pickle.dump(cfr, f)

# # UNCOMMENT - PHASE 2
num_it = int(input('Number of iterations to run: '))
with open('ph1-cfr-{}x{}.pkl'.format(num_cols, num_rows), 'rb') as f:
    cfr = pickle.load(f)

cfr.train(num_it)

dct = {
    'nodes': cfr.nodes,
    'nodes_dict': cfr.nodes_dict
}

with open('results-{}x{}-{}it.pkl'.format(num_cols, num_rows, num_it), 'wb') as f:
    pickle.dump(dct, f)