from agent.Agent import Agent

from numpy import random

class RandomAgent(Agent):
    def step(self, state):
        valid_moves = self.emptyCells(state)
        action = valid_moves[random.randint(len(valid_moves))]
        return action
    
    def emptyCells(self, state):
        res = []
        for i in range(len(state[0])):
            for j in range(len(state[1])):
                if state[i][j] == '.':
                    res.append([i, j])
        return res