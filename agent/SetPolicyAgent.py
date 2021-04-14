from agent.Agent import Agent

from numpy import random

class FixedPolicyAgent(Agent):
    def __init__(self, color):
        super().__init__(color)
        self.board_size = [3,3] # r, c
        self.opp_color = 'B' if color == 'W' else 'W'
        self.pos_moves = self._pos_moves()
        self._policy()

    def _pos_moves(self):
        moves = []
        for i in range(self.board_size[0]):
            for j in range(self.board_size[1]):
                moves.append([i, j])
        return moves
        
    def _policy(self):
        # Each entry must have as many elements as the self.pos_moves
        self.policy = [
            [0, 0, 1, 0, 0, 0, 0, 0, 0], # policy for round 1
            [0, 0, 0, .5, 0, .5, 0, 0, 0],
            [0, 0, 0, 0, 0, .5, 0, 0, .5],
        ]

    def _policy_update(self, round, history):
        extra = 0.
        for mv in history:
            c = self._convert_move(mv)
            extra += self.policy[round][c]
            self.policy[round][c] = -1
        num_zeros = len([i for i in self.policy[round] if i == 0])
        for i in range(len(self.policy[round])):
            if self.policy[round][i] == 0:
                self.policy[round][i] = extra / num_zeros
            elif self.policy[round][i] < 0:
                self.policy[round][i] = 0

    def _convert_move(self, m):
        return m[0] * self.board_size[0] + m[1]

    def step(self, round, history):
        print(round)
        if round > len(self.policy):
            raise Exception("Given policy is not complete: {} rounds of policies implemented, the function is trying to execute {}. round.".format(
                    len(self.policy), round
                ))
        self._policy_update(round, history)
        print(self.policy[round])
        action = self.pos_moves[random.choice(range(len(self.pos_moves)), p=self.policy[round])]
        return action