import numpy as np
from FSICFR import Node
import multiprocessing as mp
from tqdm import tqdm

ACCEPT = 1
DOUBT = 0

class LiarDieTrainer:
    def __init__(self, sides):
        self.sides = sides

        self.responseNodes = [[None for _ in range(self.sides+1)]
                                      for _ in range(self.sides)]
        for myClaim in range(self.sides+1):
            for oppClaim in range(myClaim+1, self.sides+1):
                self.responseNodes[myClaim][oppClaim] = \
                    Node(1 if (oppClaim == 0 or oppClaim == self.sides) else 2)

        self.claimNodes = [[None for _ in range(self.sides+1)]
                                   for _ in range(self.sides)]

        for oppClaim in range(self.sides):
            for roll in range(1, self.sides+1):
                self.claimNodes[oppClaim][roll] = Node(self.sides - oppClaim)
        
    def train(self, num_iterations):
        regret = np.zeros(self.sides)
        rollAfterAcc = np.zeros(self.sides, dtype=np.int)
        exploitability_list = []
        for num_iter in tqdm(range(num_iterations)):
            # init rolls and starting probs
            for r in range(len(rollAfterAcc)):
                rollAfterAcc[r] = np.random.randint(low=1, high=self.sides)
            self.claimNodes[0][rollAfterAcc[0]].pPlayer = 1
            self.claimNodes[0][rollAfterAcc[0]].pOpponent = 1
            
            # accumulate realization weights forward
            for oppClaim in range(self.sides+1):
                if oppClaim > 0:
                    for myClaim in range(oppClaim):
                        node = self.responseNodes[myClaim][oppClaim]
                        actionProb = node.getStrategy()
                        
                        if oppClaim < self.sides:
                            nextNode = self.claimNodes[oppClaim][rollAfterAcc[oppClaim]]
                            nextNode.pPlayer += actionProb[1] * node.pPlayer
                            nextNode.pOpponent += node.pOpponent
                if oppClaim < self.sides:
                    node = self.claimNodes[oppClaim][rollAfterAcc[oppClaim]]
                    actionProb = node.getStrategy()
                    for myClaim in range(oppClaim+1, self.sides+1):
                        nextClaimProb = actionProb[myClaim - oppClaim - 1]
                        if nextClaimProb > 0:
                            nextNode = self.responseNodes[oppClaim][myClaim]
                            nextNode.pPlayer += node.pOpponent
                            nextNode.pOpponent += node.pPlayer * nextClaimProb

            # backprop util, adjusting regrets and strg
            for oppClaim in range(self.sides, -1, -1):
                if oppClaim < self.sides:
                    node = self.claimNodes[oppClaim][rollAfterAcc[oppClaim]]
                    actionProb = node.strategy
                    node.u = 0.
                    for myClaim in range(oppClaim+1, self.sides+1):
                        actionIdx = myClaim - oppClaim - 1
                        nextNode = self.responseNodes[oppClaim][myClaim]
                        childUtil = -nextNode.u
                        regret[actionIdx] = childUtil
                        node.u += actionProb[actionIdx] * childUtil
                    for i in range(len(actionProb)):
                        regret[i] -= node.u
                        node.regretSum[i] += node.pOpponent * regret[i]
                    node.pPlayer = 0; node.pOpponent = 0

                if oppClaim > 0:
                    for myClaim in range(oppClaim):
                        node = self.responseNodes[myClaim][oppClaim]
                        actionProb = node.strategy
                        node.u = 0.
                        doubtUtil = 1 if oppClaim > rollAfterAcc[myClaim] else -1
                        regret[DOUBT] = doubtUtil
                        node.u += actionProb[DOUBT] * doubtUtil
                        if oppClaim < self.sides:
                            nextNode = self.claimNodes[oppClaim][rollAfterAcc[oppClaim]]
                            regret[ACCEPT] = nextNode.u
                            node.u += actionProb[ACCEPT] * nextNode.u
                        for i in range(len(actionProb)):
                            regret[i] -= node.u
                            node.regretSum[i] += node.pOpponent * regret[i]
                        node.pPlayer = 0; node.pOpponent = 0

            if (num_iter + 1) % 1000 == 0:
                exploitability = get_exploitability(self.claimNodes, self.responseNodes, self.sides)
                exploitability_list.append((num_iter + 1, exploitability))

            # reset strategy sums after half of training
            if num_iter == num_iterations / 2:
                for nodes in self.responseNodes:
                    for node in nodes:
                        if node:
                            for a in range(len(node.strategySum)):
                                node.strategySum[a] = 0
                for nodes in  self.claimNodes:
                    for node in nodes:
                        if node:
                            for a in range(len(node.strategySum)):
                                node.strategySum[a] = 0
                
        self.print_report()
        return exploitability_list
    
    def print_report(self):
        for initialRoll in range(1,self.sides+1):
            print('Initial claim policy with role {0}'.format(initialRoll))
            for prob in self.claimNodes[0][initialRoll].getAverageStrategy():
                print('{0:2.2f}'.format(prob))
        print('\nOld Claim\tNew Claim\tActionProbabilities')
        for myClaim in range(self.sides+1):
            for oppClaim in range(myClaim + 1, self.sides+1):
                print('\t{0}\t{1}\t\t{2}'.format(myClaim,oppClaim,self.responseNodes[myClaim][oppClaim].getAverageStrategy()))
        print('\nOld Claim\tRoll\tActionProbabilities')
        for oppClaim in range(self.sides):
            for roll in range(1,self.sides+1):
                print('{0}\t\t{1}\t{2}'.format(oppClaim,roll,str(self.claimNodes[oppClaim][roll].getAverageStrategy())))

    def strategy2df(self):
        """Things recorded about two types of strategies.
        For response nodes:
        - old claim
        - new claim
        - action probabilities to accept or reject (-1. if not available)
        For claim nodes:
        - old claim
        - roll 
        - action probabilities for the different possible claims
        """
        header = [ 'old_claim', 'new_claim', 'doubt', 'accept' ] 
        rows = []
        for prev_claim in range(self.sides + 1):
            for cur_claim in range(prev_claim + 1, self.sides + 1):
                # there is only one possible action when there is no prior claim
                # and only one possible action (i.e., ACCEPT) when the opponent 
                # claims the highest rank equal to the number of sides (i.e., DOUBT)
                node = self.responseNodes[prev_claim][cur_claim]
                assert isinstance(node, Node)

                row = [prev_claim, cur_claim]
                if cur_claim == self.sides:
                    row.append(-1.)
                    row = np.concatenate((row, node.strategy))
                else:
                    row = np.concatenate((row, node.strategy))
                rows.append(row)
        response_df = pd.DataFrame.from_records(rows, columns=header)
        response_df[['old_claim', 'new_claim']] = response_df[['old_claim', 'new_claim']].astype(int)

        header = ['old_claim', 'roll',] + [str(i) for i in range(self.sides + 1)]
        rows = []
        for old_claim in range(self.sides):
            for roll in range(1, self.sides + 1):
                # the number of legal claims remaining are the number of sides
                # minus the previous opponent claim
                node = self.claimNodes[old_claim][roll]
                assert isinstance(node, Node)
                row = [old_claim, roll] + [-1. for i in range(old_claim + 1)]
                row = np.concatenate((row, node.strategy))
                rows.append(row)
        claim_df = pd.DataFrame.from_records(rows, columns=header)
        claim_df[['old_claim', 'roll']] = claim_df[['old_claim', 'roll']].astype(int)
        return claim_df, response_df

DOUBT, ACCEPT = 0, 1
N_DIE_SIDES = 6
N_PLAYERS = 2
# doubt and accept
N_RESPONSE_ACTIONS = 2


def strategy2str(strategy, actions=None):
    str_ = ''
    for i in range(len(strategy)):
        if str_ != '':
            str_ += ', '
        action = actions[i] if actions is not None else i
        str_ += '{}: {:>6.2f}%'.format(action, strategy[i] * 100.)
    return str_


#====================================================================================================
# Exploitability
#====================================================================================================
"""To compute the exploitability metric by traversing the game tree selecting the best response strategy. This is possible because the game is 2p and zero sum.
exploitability = b_1(sigma_2) + b_2(sigma_1)
"""
def get_response_node_value(player, cur_player, old_claim, new_claim, claim_nodes, response_nodes, n_sides):
    roll_weight = 1. / n_sides
    node = response_nodes[old_claim][new_claim]
    assert isinstance(node, Node)
    next_player = 1 - cur_player
    
    # there is only one possible action, i.e., doubt
    if node.n_actions == 1:
        assert new_claim == n_sides
        # opponent's roll after accepting my old_claim
        best_action_value = 0.
        for roll in range(1, n_sides + 1):
            roll_value = 1 if new_claim > roll else -1
            best_action_value += roll_weight * roll_value
        return best_action_value

    # player is the decision maker, choose the best single action, i.e., the one with maximum regret
    best_action_value = 0.
    action_prob = node.getStrategy()
    # need to evaluate both actions and select the best one
    for roll_doubt in range(1, n_sides + 1):
        doubt_util = 1 if new_claim > roll_doubt else -1
        accept_util = get_claim_node_value_with_chance(player, cur_player, new_claim, claim_nodes, response_nodes, n_sides)

        if cur_player == player:
            roll_value = doubt_util if doubt_util >= accept_util else accept_util
        else:
            roll_value = action_prob[DOUBT] * doubt_util + action_prob[ACCEPT] * accept_util

        best_action_value += roll_weight * roll_value

    return best_action_value


def get_claim_node_value(player, cur_player, old_claim, roll, claim_nodes, response_nodes, n_sides):
    # claim nodes are never terminal nodes
    node = claim_nodes[old_claim][roll]
    assert isinstance(node, Node)
    next_player = 1 - cur_player

    # player is the decision maker, choose the best single action, i.e., the one with maximum regret
    if cur_player == player:
        if node.n_actions == 1:
            # there is only one possible action
            best_action = old_claim + 1
            best_action_value = -get_response_node_value(player, cur_player, 
                                                         old_claim, best_action, 
                                                         claim_nodes, response_nodes, n_sides)
            return best_action_value
        best_action = old_claim + 1
        best_action_value = -get_response_node_value(player, next_player,
                                                    old_claim, best_action,
                                                    claim_nodes, response_nodes, n_sides)

        for new_claim in range(old_claim + 2, n_sides + 1):
            value = -get_response_node_value(player, next_player, old_claim,
                                            new_claim, claim_nodes, response_nodes, n_sides)
            if value > best_action_value:
                best_action = new_claim
                best_action_value = value

        return best_action_value
    # current player is not the player we are computing for
    # so just weigh the child node values by their respective action probability
    else:
        value = 0.
        action_prob = node.strategy
        for new_claim in range(old_claim + 1, n_sides + 1):
            action_value = get_response_node_value(player, next_player, old_claim,
                                                   new_claim, claim_nodes, response_nodes, n_sides)
            value += action_prob[new_claim - old_claim - 1] * action_value
        return value


def get_claim_node_value_with_chance_worker(args):
    player = args['player']
    cur_player = args['cur_player']
    old_claim = args['old_claim']
    claim_nodes = args['claim_nodes']
    response_nodes = args['response_nodes'] 
    roll_arr = args['roll_arr']
    n_sides = args['n_sides']

    roll_weight = 1. / n_sides
    value = 0.
    for roll in roll_arr:
        roll_value = get_claim_node_value(player, cur_player, old_claim, roll, 
                                          claim_nodes, response_nodes, n_sides)
        value += roll_weight * roll_value
    return value


def get_claim_node_value_with_chance(player, cur_player, old_claim, 
                                     claim_nodes, response_nodes, n_sides, n_procs=1):
    value, roll_weight = 0., 1. / n_sides
    if n_procs < 1:
        n_procs = mp.cpu_count() - 1
        n_procs = n_sides if n_procs > n_sides else n_procs

    rolls = list(range(1, n_sides + 1))

    if n_procs > 1:
        roll_partition = np.array_split(rolls, n_procs)

        args_list = [{
            'player': player,
            'cur_player': cur_player,
            'old_claim': old_claim,
            'claim_nodes': claim_nodes,
            'response_nodes': response_nodes,
            'roll_arr': roll_partition[i],
            'n_sides': n_sides
        } for i in range(n_procs)]

        pool = mp.Pool(processes=n_procs)
        results = pool.map(get_claim_node_value_with_chance_worker, args_list)
        value = sum(results)
        pool.close()
    else:
        args = {
            'player': player,
            'cur_player': cur_player,
            'old_claim': old_claim,
            'claim_nodes': claim_nodes,
            'response_nodes': response_nodes,
            'roll_arr': rolls,
            'n_sides': n_sides
        } 
        value = get_claim_node_value_with_chance_worker(args)

    return value


def get_best_response_value(player, cur_player, claim_nodes, response_nodes, n_sides):
    """
    :param player int: player for which we are computing the best-response value
    :param claim_nodes array_like: claim nodes
    :param response_nodes array_like: response nodes
    :param roll_arr array_like: predetermined player rolls
    :param n_sides int: number of die sides
    """
    old_claim = 0
    next_player = 1 - cur_player
    n_procs = -1
    return get_claim_node_value_with_chance(player, next_player, old_claim, 
                                            claim_nodes, response_nodes, n_sides, n_procs)


def get_exploitability(claim_nodes, response_nodes, n_sides):
    p0_best = get_best_response_value(0, 0, claim_nodes, response_nodes, n_sides)
    p1_best = -get_best_response_value(1, 0, claim_nodes, response_nodes, n_sides)
    exploitability = p0_best + p1_best

    # info_msg = 'Best response value: p0: {:.2f}, p1: {:.2f}, Exploitability: {:.2f}'
    # info_msg = info_msg.format(p0_best, p1_best, exploitability)
    # logger.info(info_msg)

    return exploitability

#====================================================================================================
import os
import pandas as pd
    
if __name__ == '__main__':
    n_iter = 1000000
    N_DIE_SIDES = 6
    trainer = LiarDieTrainer(N_DIE_SIDES)

    exploitability_list = trainer.train(n_iter)

    claim_df, response_df = trainer.strategy2df()

    outdir = os.path.join('results', 'liar-die-fsicfr')
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    claim_fname = 'liar-die-fsicfr-n_die_sides_{}-it_{}-claim.csv'
    claim_fname = claim_fname.format(trainer.sides, n_iter)
    claim_fp = os.path.join(outdir, claim_fname)
    claim_df.to_csv(claim_fp, index=None, float_format='%.5f')

    response_fname = 'liar-die-fsicfr-n_die_sides_{}-it_{}-response.csv'
    response_fname = response_fname.format(trainer.sides, n_iter)
    response_fp = os.path.join(outdir, response_fname)
    response_df.to_csv(response_fp, index=None, float_format='%.5f')

    exploitability_fname = 'liar-die-fsicfr-n_die_sides_{}-it_{}-exploitability.csv'
    exploitability_fname = exploitability_fname.format(trainer.sides, n_iter)
    exploitability_fp = os.path.join(outdir, exploitability_fname)
    
    columns = ['iteration', 'exploitability']
    exploitability_df = pd.DataFrame.from_records(exploitability_list, columns=columns)
    exploitability_df['iteration'] = exploitability_df['iteration'].astype(int)
    exploitability_df.to_csv(exploitability_fp, index=None, float_format='%.5f')