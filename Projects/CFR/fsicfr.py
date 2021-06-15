import numpy as np
from Projects.base.util.print_tools import seq_to_str
from Projects.base.game.darkHex import DarkHex
from tqdm import tqdm
from copy import deepcopy
from Projects.base.util.colors import pieces

class Node:
    def __init__(self, board1, board2, player, num_actions) -> None:
        # FIX: Player is 0/1 - Might need B/W instead
        self.player = player
        self.num_actions = num_actions
        self.board1 = board1
        self.board2 = board2

        self.board = self.board1 if self.player == 0 else self.board2

        self.strategy = np.zeros(num_actions)
        self.regretSum = np.zeros(num_actions)
        self.strategySum = np.zeros(num_actions)

        self.T = 0
        self.u = 0
        self.pSum1 = 1
        self.pSum2 = 1

        self.pos_actions = [x for x in self.board if x == pieces.NEUTRAL]

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
                self.strategy[a] = 1 / len(self.pos_actions)
            self.strategySum[a] += self.strategy[a] * (self.pSum1 if self.player == 0 else self.pSum2)
            # * summing up all the action probabilities
            # ? what is realizationWeight again
        return self.strategy

    def getAverageStrategy(self):
        normalizingSum = 0
        for a in range(len(self.strategySum)):
            normalizingSum += self.strategySum[a]
            # summing up all the action probs using strategySum
            # ? why strategySum
        for a in range(len(self.strategySum)):
            if normalizingSum > 0:
                self.strategySum[a] /= normalizingSum
            else:
                self.strategySum[a] = 1 / len(self.strategySum)
        return self.strategySum

    def __str__(self):
        return "{}:\t{}".format(self.infoset, seq_to_str(self.getAverageStrategy(), spacing=' '))


class FSICFR:
    def __init__(self, num_rows=3, num_cols=3) -> None:
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_actions = num_cols * num_rows
        self.nodes = self.__init_board_topSorted()

    def train(self, num_of_iterations) -> None:
        regret = [0.0 for _ in range(self.num_of_actions)]
        for it in num_of_iterations:
            for node in self.nodes: # top-sorted nodes
                strategy = node.getStrategy()
                game = DarkHex(BOARD_SIZE=[self.num_rows, self.num_cols], 
                               custom_board_C_PLAYER1=node.board1,
                               custom_board_C_PLAYER2=node.board2,
                               verbose=False)
                for a in range(self.num_of_actions): # for each possible move
                    # take action a
                    _, _, res, _ = game.step(node.player, a)
                    if res == 'f':
                        game.rewind()
                        continue
                    infoset_c = self.find_infoset(self.game)
                    game.rewind()
                    # update visits
                    self.nodes[infoset_c].visits += node.visits
                    # update the rweights
                    self.nodes[infoset_c].pSum1 += (strategy[a] * node.pSum1 if node.player == 0 else node.pSum2)
                    self.nodes[infoset_c].pSum2 += (strategy[a] * node.pSum2 if node.player == 1 else node.pSum1)
            # endfor - nodes
            nodes_rev = self.nodes[::-1]
            for node in nodes_rev:
                game = DarkHex(BOARD_SIZE=[self.num_rows, self.num_cols], 
                               custom_board_C_PLAYER1=node.board1,
                               custom_board_C_PLAYER2=node.board2,
                               verbose=False)
                if game.game_status == pieces.C_PLAYER1:
                    if node.player == 0:
                        node.u = 1
                    else:
                        node.u = -1
                elif game.game_status == pieces.C_PLAYER2:
                    if node.player == 1:
                        node.u = 1
                    else:
                        node.u = -1
                else:
                    for a in node.pos_actions:
                        _, _, res, _ = self.game.step(node.player, a)
                        if res == 'f':
                            game.rewind()
                            continue
                        infoset_c = self.find_infoset(game)
                        game.rewind()
                        if self.nodes[infoset_c].player == node.player:
                            childUtil = self.nodes[infoset_c].u
                        else:
                            childUtil = - self.nodes[infoset_c].u
                        regret[a] = childUtil
                        node.u += node.strategy[a] * childUtil
                    cfp = node.pSum1 if node.player == 0 else node.pSum2
                    for a in node.pos_actions:
                        nomin = (node.T * node.regretSum[a] + node.visits * cfp * (regret[a] - node.u))
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
                        
    def __init_board_topSorted(self) -> list:
        # ls = []
        game = DarkHex([2, 2], True)
        for a in game.valid_moves_colors[pieces.C_PLAYER1]:
            game.step(pieces.C_PLAYER1, a)
            game.print_information_set(pieces.C_PLAYER1)
            game.print_information_set(pieces.C_PLAYER2)
            game.rewind()
        # return ls

cfr = FSICFR()