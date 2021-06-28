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
        for it in tqdm(range(num_of_iterations)):
        # for it in range(num_of_iterations):
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
                        if self.__is_board_legal_wTerminal(new_board, rev_player, node.player, node.h-1):
                            children.append(get_infoset(node.player, new_board, node.h-1))
                    new_board = self.__add_stone(node.board, a, node.player)
                    if self.__is_board_legal_wTerminal(new_board, rev_player, node.player, node.h):
                        children.append(get_infoset(node.player, new_board, node.h))
                    for infoset_c in children:
                        # update visits
                        # if infoset_c not in self.nodes_dict:
                        #     continue
                        # if self.nodes_dict[infoset_c].board == ['B', 'W', '.', 'B'] and self.nodes_dict[infoset_c].player == 'W':
                        #     print('here')
                        #     pass
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
                        if self.__is_board_legal_wTerminal(new_board, rev_player, node.player, node.h):
                            children.append(get_infoset(node.player, new_board, node.h))
                        if node.h > 0:
                            new_board = self.__add_stone(node.board, a, rev_player)
                            if self.__is_board_legal_wTerminal(new_board, rev_player, node.player, node.h-1):
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
            if not node.is_terminal:
                print(node.infoSet, node.getAverageStrategy())
                        
    def __init_board_topSorted(self) -> list:
        # ! Remove more states using pONE

        # FIX: THERE R EXTRA STATE NODES - FIND THE MISTAKE & REMOVE THEM
        ls = []
        nodes = {}
        visited = defaultdict(lambda: False)
        game = DarkHex([self.num_rows, self.num_cols], False)
        self.__topSort_play(game, ls, visited)

        for i in range(len(ls)-1, -1, -1):
            nodes[ls[i].infoSet] = ls[i]
        print("Phase 1 has ended...")
        print("{} number of unique states".format(len(nodes)))
        return ls, nodes

    def __topSort_play(self, game, stack, visited) -> None:
        player = game.turn_info()
        rev_player = pieces.C_PLAYER1 if player == pieces.C_PLAYER2 else pieces.C_PLAYER2
        valid_moves = copy(game.valid_moves_colors[player])
        for a in valid_moves:
            _, _, res, _ = game.step(player, a)
            if res == 'f':
                node = Node(board=game.BOARDS[player], 
                            move_history=game.move_history[player],
                            player=player, 
                            h=game.totalHidden_for_player(player))
                ext_infoSet = tuple([*game.BOARDS[game.C_PLAYER1], *game.BOARDS[game.C_PLAYER2]])
                if not self.__is_board_legal(game.BOARDS[player], rev_player, player, node.h):
                    game.rewind()
                    continue
                # if visited[node.infoSet]:
                if visited[ext_infoSet]:
                    game.rewind(True)
                    continue
                else:
                    # visited[node.infoSet] = True
                    visited[ext_infoSet] = True
                    self.__topSort_play(game, stack, visited)
                    stack.append(node)
                    game.rewind(True)
                continue
            # * CREATING THE NODE
            if game.game_status() != '=':
                new_h = game.totalHidden_for_player(player)
                is_terminal = True
            else:
                new_h = game.totalHidden_for_player(player)+1
                is_terminal = False
            node = Node(board=game.BOARDS[player], 
                        move_history=game.move_history[player],
                        player=player, 
                        h=new_h)                     
            node.is_terminal = is_terminal
            # *******************
            ext_infoSet = tuple([*game.BOARDS[game.C_PLAYER1], *game.BOARDS[game.C_PLAYER2]])
            if not self.__is_board_legal(game.BOARDS[player], rev_player, player, new_h):
                # * There is a special case here. We are checking one step ahead to see if the 
                # * board is legal. This means two moves for general game, one move for the player
                # * other players move might be legal even if current players is not.
                if not self.__is_board_legal(game.BOARDS[rev_player], player, rev_player, game.totalHidden_for_player(rev_player)):
                    game.rewind()
                    continue
            if visited[ext_infoSet]:
            # if visited[node.infoSet]:
                game.rewind()
            else:
                # visited[node.infoSet] = True
                visited[ext_infoSet] = True
                if not node.is_terminal:
                    self.__topSort_play(game, stack, visited)
                stack.append(node)
                game.rewind()

    def __add_stone(self, board, action, player):
        new_board = deepcopy(board)
        new_board[action] = player
        return new_board

    def __is_board_legal(self, board, rev_player, player_turn, h):
        # player is the player which owns the turn
        game = Hex(BOARD_SIZE=[self.num_rows, self.num_cols], BOARD=board,
                   legality_check=True, h_player=rev_player, h=h)
        res = game.game_status()
        
        ct = game.BOARD.count('.')
        if res == 'i' or game.turn_info() != player_turn or\
            ct <= h:
            # illegal game
            return False        
        return True

    def __is_board_legal_wTerminal(self, board, rev_player, player_turn, h):
        # player is the player which owns the turn
        game = Hex(BOARD_SIZE=[self.num_rows, self.num_cols], BOARD=board,
                   legality_check=True, h_player=rev_player, h=h)
        res = game.game_status()
        
        ct = game.BOARD.count('.')
        if res in ['i', rev_player] or\
            game.turn_info() != player_turn or\
            ct <= h:
            # illegal game
            return False        
        return True


def get_infoset(player, board, h) -> tuple:
    return tuple([player, *board, h])

def get_infoset_extended(board1, board2) -> tuple:
    return tuple([*board1, *board2])

num_cols = 3
num_rows = 3

# UNCOMMENT - PHASE 1
cfr = FSICFR(num_cols=num_cols, num_rows=num_rows)

with open('ph1-cfr-{}x{}.pkl'.format(num_cols, num_rows), 'wb') as f:
    pickle.dump(cfr, f)


# # UNCOMMENT - PHASE 2
num_it = 100
with open('ph1-cfr-{}x{}.pkl'.format(num_cols, num_rows), 'rb') as f:
    cfr = pickle.load(f)

cfr.train(num_it)

dct = {
    'nodes': cfr.nodes,
    'nodes_dict': cfr.nodes_dict
}

with open('results-{}x{}-{}it.pkl'.format(num_cols, num_rows, num_it), 'wb') as f:
    pickle.dump(dct, f)