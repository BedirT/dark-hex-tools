import numpy as np
from Projects.base.util.print_tools import seq_to_str
from Projects.base.game.darkHex import DarkHex
from Projects.base.game.hex import Hex
from tqdm import tqdm
from copy import deepcopy, copy
from Projects.base.util.colors import pieces
from collections import defaultdict

class Node:
    def __init__(self, board, move_history, player, h) -> None:
        self.player = player
        self.num_actions = len(board)
        self.move_history = move_history
        self.board = deepcopy(board)
        self.h = h

        # self.infoSet = self.player + '-' + seq_to_str(self.move_history) + '-' +  seq_to_str(self.board) +'-' +  str(h)
        self.infoSet = get_infoset(self.player, self.board, self.h)

        self.strategy = np.zeros(self.num_actions)
        self.regretSum = np.zeros(self.num_actions)
        self.strategySum = np.zeros(self.num_actions)

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
        self.nodes, self.nodes_dict = self.__init_board_topSorted()

    def train(self, num_of_iterations) -> None:
        regret = [[0.0, 0.0] for _ in range(self.num_actions)]
        for it in range(num_of_iterations):
            for node in self.nodes: # top-sorted nodes
                if node.is_terminal:
                    continue
                rev_player = pieces.C_PLAYER1 if node.player == pieces.C_PLAYER2 else pieces.C_PLAYER2
                strategy = node.getStrategy()
                for a in node.pos_actions: # for each possible move
                    # take action a on board
                    children = []
                    # * update the board with action a and add the new
                    # * board state to the -children- to traverse later
                    if node.h > 0:
                        new_board = self.__add_stone(node.board, a, rev_player)
                        if self.__is_board_legal(new_board, rev_player, node.player):
                            children.append(get_infoset(node.player, new_board, node.h-1))
                    new_board = self.__add_stone(node.board, a, node.player)
                    if self.__is_board_legal(new_board, rev_player, node.player):
                        children.append(get_infoset(node.player, new_board, node.h))
                    for infoset_c in children:
                        # update visits
                        # if infoset_c not in self.nodes_dict:
                        #     continue
                        self.nodes_dict[infoset_c].visits += node.visits
                        # update the rweights
                        # print(strategy[a], node.pSum1, node.pSum2)
                        self.nodes_dict[infoset_c].pSum1 += (strategy[a] * node.pSum1 if node.player == pieces.C_PLAYER1 else node.pSum2)
                        self.nodes_dict[infoset_c].pSum2 += (strategy[a] * node.pSum2 if node.player == pieces.C_PLAYER2 else node.pSum1)
                        # print(strategy[a], node.pSum1, node.pSum2)
                        # print(self.nodes_dict[infoset_c].pSum1, self.nodes_dict[infoset_c].pSum2)
                        # print(infoset_c)
                        pass
                # endfor - pos_actions
            # endfor - nodes
            for node in self.nodes[::-1]:
                rev_player = pieces.C_PLAYER1 if node.player == pieces.C_PLAYER2 else pieces.C_PLAYER2
                game = Hex(BOARD_SIZE=[self.num_rows, self.num_cols],
                           BOARD=node.board, verbose=False)
                if game.game_status() == node.player:
                    node.u = 1
                elif game.game_status() != '=':
                    node.u = -1
                else:
                    for a in node.pos_actions:
                        children = []
                        # * update the board with action a and add the new
                        # * board state to the -children- to traverse later
                        new_board = self.__add_stone(node.board, a, node.player)
                        if self.__is_board_legal(new_board, rev_player, node.player):
                            children.append(get_infoset(node.player, new_board, node.h))
                        if node.h > 0:
                            new_board = self.__add_stone(node.board, a, rev_player)
                            if self.__is_board_legal(new_board, rev_player, node.player):
                                children.append(get_infoset(node.player, new_board, node.h-1))
                        for i, infoset_c in enumerate(children):
                            if self.nodes_dict[infoset_c].player == node.player:
                                childUtil = self.nodes_dict[infoset_c].u
                            else:
                                childUtil = - self.nodes_dict[infoset_c].u
                            regret[a][i] = childUtil
                            node.u += node.strategy[a] * childUtil
                    cfp = node.pSum1 if node.player == pieces.C_PLAYER1 else node.pSum2
                    # print(cfp)
                    for h_stat in range(2):
                        for a in node.pos_actions:
                            nomin = (node.T * node.regretSum[a] + node.visits * cfp * (regret[a][h_stat] - node.u))
                            denom = node.T + node.visits
                            node.regretSum[a] = nomin / denom
                        node.T += node.visits

            # node.visits = 0
            # node.pSum1 = 0
            # node.pSum2 = 0
            
            # reset the strategysums - page 32
            if it == num_of_iterations//2:
                for node in self.nodes:
                    for a in range(len(node.strategySum)):
                        node.strategySum[a] = 0

        for node in self.nodes:
            print(node.infoSet, node.getAverageStrategy())
                        
    def __init_board_topSorted(self) -> list:
        # ! Remove more states using pONE

        # FIX: THERE R EXTRA STATE NODES - FIND THE MISTAKE & REMOVE THEM
        ls = []
        nodes = {}
        visited = defaultdict(lambda: False)
        game = DarkHex([self.num_rows, self.num_cols], False)
        self.__topSort_play(game, 0, ls, visited)

        for i in range(len(ls)-1, -1, -1):
            nodes[ls[i].infoSet] = ls[i]
        # print(len(nodes))
        return ls, nodes

    def __topSort_play(self, game, turn, stack, visited) -> None:
        player = pieces.C_PLAYER1 if turn % 2 == 0 else pieces.C_PLAYER2
        rev_player = pieces.C_PLAYER1 if player == pieces.C_PLAYER2 else pieces.C_PLAYER1
        # if not self.__is_board_legal(game.BOARD, rev_player, player):
        #     return
        valid_moves = copy(game.valid_moves_colors[player])
        for a in valid_moves:
            if game.BOARDS[player][a] != '.':
                print('Fail', valid_moves, a, game.BOARDS[player])
                exit()
            _, _, res, _ = game.step(player, a)
            if res == 'f':
                node = Node(board=game.BOARDS[player], 
                            move_history=game.move_history[player],
                            player=player, 
                            h=game.totalHidden_for_player(player))
                if visited[node.infoSet]:
                    game.rewind(True)
                    continue
                else:
                    visited[node.infoSet] = True
                    self.__topSort_play(game, turn, stack, visited)
                    stack.append(node)
                    game.rewind(True)
                continue
            # * CREATING THE NODE
            new_h = game.totalHidden_for_player(player)+1
            is_terminal = False
            if game.game_status() != '=':
                new_h -= 1
                is_terminal = True
            node = Node(board=game.BOARDS[player], 
                        move_history=game.move_history[player],
                        player=player, 
                        h=new_h)
            node.is_terminal = is_terminal
            # *******************
            if visited[node.infoSet]:
                game.rewind()
                continue
            else:
                visited[node.infoSet] = True
                if not node.is_terminal:
                    self.__topSort_play(game, turn+1, stack, visited)
                stack.append(node)
                game.rewind()
                pass

    def __add_stone(self, board, action, player):
        new_board = deepcopy(board)
        new_board[action] = player
        return new_board

    def __is_board_legal(self, board, rev_player, player_turn):
        # player is the player which owns the turn
        game = Hex(BOARD_SIZE=[self.num_rows, self.num_cols], BOARD=board,
                   legality_check=True, h_player=rev_player, early_w_p1=True,
                   early_w_p2=True)
        res = game.game_status()
        if res != '=' or game.turn_info() != player_turn:
            # illegal game
            return False        
        return True


def get_infoset(player, board, h) -> tuple:
    return tuple([player, *board, h])

cfr = FSICFR(num_cols=2, num_rows=2)
cfr.train(1000)