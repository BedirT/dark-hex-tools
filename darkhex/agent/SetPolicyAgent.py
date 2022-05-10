from Projects.base.agent.Agent import Agent

from numpy import random
import copy


class PolicyPerRound:

    def __init__(self, policy, children=[], children_prob=[]):
        self.board_size = [3, 4]
        self.policy = policy
        self.children = children
        self.children_prob = children_prob

        self.random_policy = False

    def _policy_elements(self, pol_to_check):
        ls = []
        for i, p in enumerate(pol_to_check):
            if p > 0:
                ls.append(i)
        return ls

    def next_move(self, state, ct):
        if self.children_prob:
            return self._valid_children_wProb(state)
        try:
            return self._valid_children(state)[ct]
        except:
            print('Given strategy is not complete. Playing randomly.')
            return None

    def _valid_children_wProb(self, state):
        valid = []
        valid_prob = []
        for i, ch in enumerate(self.children):
            if any(x in self._policy_elements(ch.policy)
                   for x in self._occupied_cells(state)):
                continue
            elif self.children_prob[i] == -1:
                # prioritize and change the prob
                self.children_prob[i] = 0
                return ch
            else:
                valid.append(ch)
                valid_prob.append(self.children_prob[i])
        return valid[random.choice(range(len(valid)), p=valid_prob)]

    def _valid_children(self, board_state):
        # might need change
        valid = []
        for ch in self.children:
            if any(x in self._policy_elements(ch.policy)
                   for x in self._occupied_cells(board_state)):
                continue
            else:
                valid.append(ch)
        return valid

    def _occupied_cells(self, board):
        ls = []
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] != '.':
                    ls.append(self._convert_move([i, j]))
        return ls

    def _add_children(self, new_children):
        self.children += new_children

    def _convert_move(self, m):
        return m[0] * self.board_size[1] + m[1]


class FixedPolicyAgent_wTree(Agent):

    def __init__(self, color, pos_moves):
        super().__init__(color)
        self.board_size = [3, 4]  # r, c
        self.opp_color = 'B' if color == 'W' else 'W'
        self.policy = self._create_policy_tree()
        self.pos_moves = copy.deepcopy(pos_moves)
        self.count = 0

    def _create_policy_tree(self):
        # ISO 1
        z0 = PolicyPerRound([0, 0, 0, 0, 0, 0, 0, .5, 0, 0, 0, .5])
        z1 = PolicyPerRound([0, 0, 0, 0, 0, 0, 0, 0, 0, .5, .5, 0],
                            children=[z0])
        z1 = PolicyPerRound([0, 0, 0, 0, 0, 0, 0, 0, 0, .5, .5, 0],
                            children=[z1])

        y1 = PolicyPerRound([0, 0, .5, .5, 0, 0, 0, 0, 0, 0, 0, 0])
        y1 = PolicyPerRound([0, 0, .5, .5, 0, 0, 0, 0, 0, 0, 0, 0],
                            children=[y1])

        # if C2 was empty
        x0 = PolicyPerRound([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, .5, .5])
        x0 = PolicyPerRound([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, .5, .5],
                            children=[x0])
        x = PolicyPerRound([0, 0, 0, .5, 0, 0, 0, .5, 0, 0, 0, 0])
        x = PolicyPerRound([0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                           children=[x, x0])

        x = PolicyPerRound([0, 0, 0, 0, .5, 0, 0, 0, .5, 0, 0, 0],
                           children=[x, y1, z1],
                           children_prob=[-1, 0.5, 0.5])
        xx = PolicyPerRound([0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0], children=[x])

        # ISO 2
        z0 = PolicyPerRound([.5, 0, 0, 0, .5, 0, 0, 0, 0, 0, 0, 0])
        z1 = PolicyPerRound([0, .5, .5, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            children=[z0])
        z1 = PolicyPerRound([0, .5, .5, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            children=[z1])

        y1 = PolicyPerRound([0, 0, 0, 0, 0, 0, 0, 0, .5, .5, 0, 0])
        y1 = PolicyPerRound([0, 0, 0, 0, 0, 0, 0, 0, .5, .5, 0, 0],
                            children=[y1])

        # # if C2 was empty
        x0 = PolicyPerRound([.5, .5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        x0 = PolicyPerRound([.5, .5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            children=[x0])
        x = PolicyPerRound([0, 0, 0, 0, .5, 0, 0, 0, .5, 0, 0, 0])
        x = PolicyPerRound([0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                           children=[x, x0])

        x = PolicyPerRound([0, 0, 0, .5, 0, 0, 0, .5, 0, 0, 0, 0],
                           children=[x, y1, z1],
                           children_prob=[-1, 0.5, 0.5])
        x = PolicyPerRound([0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], children=[x])
        root = PolicyPerRound(policy=[],
                              children=[x, xx],
                              children_prob=[.5, .5])

        return root

    def _next_policy(self, obs):
        self.policy = self.policy.next_move(obs, self.count)

    def _policy_update(self, obs):
        p = self.policy.policy
        extra = 0.
        for i in range(len(obs)):
            for j in range(len(obs[i])):
                if obs[i][j] != '.':
                    c = self._convert_move([i, j])
                    if p[c] > 0:
                        extra += p[c]
                        p[c] = -1
        num__pos_elements = len([i for i in p if i > 0])
        suc = False
        for i in range(len(p)):
            if p[i] > 0:
                p[i] += extra / num__pos_elements
                suc = True
            elif p[i] < 0:
                p[i] = 0
        return suc  # return if there is any positive values

    def _convert_move(self, m):
        return m[0] * self.board_size[1] + m[1]

    def step(self, observation, success):
        try:
            if not success:
                v = self._policy_update(observation)
                if not v:
                    self.count += 1
                    self._next_policy(observation)
                # move
            else:
                self.count = 0
                self._next_policy(observation)
            action = self.pos_moves[random.choice(range(len(self.pos_moves)),
                                                  p=self.policy.policy)]
            return action
        except:
            p = [1 / (self.board_size[0] * self.board_size[1])] \
                 * (self.board_size[0] * self.board_size[1])
            action = self.pos_moves[random.choice(range(len(self.pos_moves)),
                                                  p=p)]
            return action


class FixedPolicyAgent(Agent):

    def __init__(self, color):
        super().__init__(color)
        self.board_size = [3, 4]  # r, c
        self.opp_color = 'B' if color == 'W' else 'W'
        self.pos_moves = self._pos_moves()

        # Each entry must have as many elements as the self.pos_moves
        self.policy = [
            [
                [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            ],  # policies for round 1
            [
                [0, 0, 0, 0, .5, 0, 0, 0, .5, 0, 0, 0],
            ],  # round 2
            [
                [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, .25, .25, 0, 0, 0, 0, 0, .25, .25, 0],
            ],  # round 3
            [
                [0, 0, .25, .25, 0, 0, 0, 0, 0, 0, 0, 0],
            ]  # round 4
        ]
        self.games = [  # the strategies used by the player
            # for each round
            [[0], [0], [1], [0]],
            [[0], [0], [0], [1]],
        ]
        self.policies_followed = []  # correct it

    def _pos_moves(self):
        moves = []
        for i in range(self.board_size[0] * self.board_size[1]):
            moves.append(i)
        return moves

    def _get_valid_games(self):
        valid_games = []
        for game in self.games:
            #   [[0], [0], [1], [0]]
            #   [0,0,0,0]
            flag = True
            for r in range(len(self.policies_followed)):
                # for each policy in the current round we are checking
                # (in the current game)
                # [0] - for round 0
                if game[r] != self.policies_followed[r]:
                    # the game is clear so far
                    flag = False
            if flag:
                valid_games.append(game)
        return valid_games

    def _policy(self, round, history):
        games = self._get_valid_games()
        game = games[random.choice(range(len(games)))]
        r_policy = self._policy_update(game, round, history)
        return self._check_first_valid_policy(r_policy)

    def _check_first_valid_policy(self, policies_to_check):
        for p in policies_to_check:
            if not all(v == 0 for v in p):
                return p
        # no policies are good for current state
        # so we move randomly
        return [1 / (self.board_size[0] * self.board_size[1])] \
                  * (self.board_size[0] * self.board_size[1])

    def _policy_update(self, game, round, history):
        print(game[round])
        for r in game[round]:
            round_policy = copy.deepcopy(self.policy[round][r])
            for p in round_policy:
                extra = 0.
                for mv in history:
                    c = self._convert_move(mv)
                    extra += p[c]
                    p[c] = -1
                num__pos_elements = len([i for i in p if i > 0])
                for i in range(len(p)):
                    if p[i] > 0:
                        p[i] += extra / num__pos_elements
                    elif p[i] < 0:
                        p[i] = 0
            return round_policy

    def _convert_move(self, m):
        return m[0] * self.board_size[0] + m[1]

    def step(self, round, history):
        print(round)
        if round > len(self.policy):
            raise Exception(
                "Given policy is not complete: {} rounds of policies implemented, the function is trying to execute {}. round."
                .format(len(self.policy), round))
        policy = self._policy(round, history)
        action = self.pos_moves[random.choice(range(len(self.pos_moves)),
                                              p=policy)]
        # update policies followed. Fixx this
        self.policies_followed.append(action)
        return action
