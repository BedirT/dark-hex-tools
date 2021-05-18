# FSICFR implementation on DarkHex
class Node:
    # we will assume its a 2x2 board
    # we will have 4 moves, [0,1,2,3]
    # no chance nodes
    def __init__(self, num_of_action):
        # self.num_cols = board_size[1]
        # self.num_rows = board_size[0]
        self.n_actions = num_of_action
        # self.n_actions = self.num_cols * self.num_rows

        self.u = 0.
        self.pPlayer = 0.
        self.pOpponent = 0.
        
        self.regretSum = [0. for _ in range(self.n_actions)]
        self.strategy = [0. for _ in range(self.n_actions)]
        self.strategySum = [0. for _ in range(self.n_actions)]

    def getStrategy(self):
        normalizingSum = 0.
        for s in range(len(self.strategy)):
            self.strategy[s] = max(self.regretSum[s], 0)
            normalizingSum += self.strategy[s]

        for s in range(len(self.strategy)):
            if normalizingSum > 0:
                self.strategy[s] /= normalizingSum
            else:
                self.strategy[s] = 1/len(self.strategy)             

        for s in range(len(self.strategySum)):
            self.strategySum[s] += self.pPlayer * self.strategySum[s]

        return self.strategy

    def getAverageStrategy(self):
        normalizingSum = sum([s for s in self.strategySum])

        for s in range(len(self.strategySum)):
            if normalizingSum > 0:
                self.strategySum[s] /= normalizingSum
            else:
                self.strategySum[s] = 1./len(self.strategySum)
        
        return self.strategySum    