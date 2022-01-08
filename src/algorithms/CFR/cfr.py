from copy import deepcopy, copy
import numpy as np
from Projects.base.util.print_tools import seq_to_str
from Projects.base.game.darkHex import DarkHex
from tqdm import tqdm

class Node:
    def __init__(self, num_actions) -> None:
        self.num_actions = num_actions

        self.infoset = ""
        self.strategy = np.zeros(num_actions)
        self.regretSum = np.zeros(num_actions)
        self.strategySum = np.zeros(num_actions)

        self.pos_actions = [*range(num_actions)]

    def getStrategy(self, realizationWeight): 
        # ? What is realizationWeight
        normalizingSum = 0
        for a in self.pos_actions:
            self.strategy[a] = self.regretSum[a] if self.regretSum[a] > 0 else 0 # ? where do we change regretSum
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
            self.strategySum[a] += realizationWeight * self.strategy[a] 
            # * summing up all the action probabilities
            # ? what is realizationWeight again
        return self.strategy

    def getAverageStrategy(self):
        avgStrategy = np.zeros(self.num_actions)
        normalizingSum = 0
        for a in self.pos_actions:
            normalizingSum += self.strategySum[a]
            # summing up all the action probs using strategySum
            # ? why strategySum
        for a in self.pos_actions:
            if normalizingSum > 0:
                avgStrategy[a] = self.strategySum[a] / normalizingSum
            else:
                avgStrategy[a] = 1 / len(self.pos_actions)
        return avgStrategy

    def __str__(self):
        return "{}:\t{}".format(self.infoset, seq_to_str(self.getAverageStrategy(), spacing=' '))


class CFRTrainer:
    def __init__(self, game, args=[]) -> None:
        self.game = game(*args)
        self.nodeMap = {}

        self.win_reward = 1
        self.loss_reward = -1

        self.ct = 0

    def train(self, num_iterations) -> None:
        util = 0

        # for _ in range(num_iterations):
        for _ in tqdm(range(num_iterations)):
            util += self.cfr(self.game, 1, 1)
        
        print("Average game value: " + str(util / num_iterations))
        for n in self.nodeMap:
            print(self.nodeMap[n])

    def cfr(self, game, p0, p1, a=-1):
        game = deepcopy(game)
        player = game.turn_info()
        if a != -1:
            _, _, res, _ = game.step(player, a)
            if res == 'f':
                return False
        game_stat = game.game_status()
        if game_stat != '=': # TERMINAL
            # if game_stat == game.C_PLAYER1:
            if game_stat == game.C_PLAYER1:
                return self.win_reward
            else:
                return self.loss_reward

        oppPlayer = game.rev_color[player]
        infoSet = player + '{0:-<{1}}'.format(seq_to_str(game.move_history[player]), game.num_cells) \
                         + seq_to_str(game.BOARDS[player]) + str(game.totalHidden_for_player(player))
        # infoSet = oppPlayer + '{0:-<{1}}'.format(seq_to_str(game.move_history[oppPlayer]), game.num_cells) \
        #                  + seq_to_str(game.BOARDS[oppPlayer]) + str(game.totalHidden_for_player(oppPlayer))
        # * setting the dictionary for the infoset node
        # * or create it if non existent
        if infoSet in self.nodeMap:
            node = self.nodeMap[infoSet]
        else:
            self.ct += 1
            node = Node(num_actions=game.num_cells)
            node.infoset = infoSet
            self.nodeMap[infoSet] = node

        strategy = node.getStrategy(p0 if player == game.C_PLAYER1 else p1)
        util = np.zeros_like(strategy)
        nodeUtil = 0
        
        valid_moves = game.valid_moves_colors[player]
        for a in valid_moves:
            if player == game.C_PLAYER1:
                res = self.cfr(game, p0 * strategy[a], p1, a)
                if not res: continue
                util[a] = res
            else:
                res = self.cfr(game, p0, p1 * strategy[a], a)
                if not res: continue
                util[a] = res
            # game.rewind()
            nodeUtil += strategy[a] * util[a]
        
        for a in valid_moves:
            regret = util[a] - nodeUtil
            node.regretSum[a] += (p1 if player == game.C_PLAYER1 else p0) * regret

        return nodeUtil

def str_to_tup(s):
    l = []
    for i in s:
        l.append(i)
    return tuple(l)

cfr = CFRTrainer(DarkHex, [[3,3], False])
cfr.train(10000)
print(cfr.ct)