from Projects.base.agent.Agent import Agent

from numpy import random


class RandomAgent(Agent):

    def step(self, state):
        valid_moves = [i for i, x in enumerate(state) if x == '.']
        action = random.choice(valid_moves)
        return action
