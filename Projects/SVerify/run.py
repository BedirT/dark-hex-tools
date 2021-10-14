'''
Strategy Verifier
-----------------
This program evaluates the performance of a strategy S for player p
against every possible strategy S' for player p', on the game DarkHex.

Strategy S is given as a {information set: [(action, probability), ...]}
Strategy S' is every legal move possible at the given game position.

The program works in a linear logic. p makes its move as long as S has
a move to make, if ANY branch stops in a tied position, the strategy is
incomplete. Otherwise the program returns the probability of the winning
for the player p.

Parameters:
    -p: player to evaluate
    -S: strategy to evaluate
'''
from Projects.base.game.darkHex import DarkHex
from Projects.base.game.hex import pieces
from strategy_data import strategies

PROBS = {}
incomplete = False

def start_the_game(game, p_order, S, p_color, o_color, player_turn):
    '''
    Plays the game until all the S moves are exhausted
    recursively calls itself. If the game is tied, the strategy is incomplete.
    Recursively calculates the probability of winning for player p.
    '''
    global incomplete
    if incomplete:
        return False
    p_res = 0 # probability of p winning for the current branch
    # p plays according to its order (0 or 1)
    if player_turn == p_order:
        # p plays ALL the next moves for the current
        # information set for p
        if game.get_information_set(p_color) not in S:
            # p has no moves, the game is tied
            # S is incomplete)
            print('{}\n{}'.format(game.get_information_set(p_color), game.BOARD))
            incomplete = True
            return False
        for action in S[game.get_information_set(p_color)]:
            prob = 1 / len(S[game.get_information_set(p_color)])
            _, res, _ = game.step(p_color, action)
            # game.printBoard()
            if res == p_color:
                # p wins
                p_res += prob
                # rewind the game
                game.rewind()
            else:
                # continue playing the game
                if res == pieces.kFail:
                    p_res += prob * start_the_game(game, p_order, S, p_color, o_color, player_turn)
                else:
                    p_res += prob * start_the_game(game, p_order, S, p_color, o_color, (player_turn + 1) % 2)
                # rewind the game
                game.rewind()
        return p_res
    else:
        # o plays ALL legal moves for the current information set for o
        # we are assuming this player always plays the best move possible
        # so if there is a win for o, then o wins the branch
        pos_results = []
        for action in game.valid_moves:
            _, res, _ = game.step(o_color, action)
            if res == o_color:
                # o wins
                game.rewind()
                return 0
            else:
                # continue playing the game
                pos_results.append(start_the_game(game, p_order, S, p_color, o_color, (player_turn + 1) % 2))
                # rewind the game
                game.rewind()
        return min(pos_results)

def main(): 
    strategy_dict = strategies.ryan_3x4_lower_bound
    game = DarkHex(BOARD_SIZE=strategy_dict['board_size'],
                    verbose=False)
    player = strategy_dict['player'] # player to evaluate
    p_order = strategy_dict['player_order'] # the order of the player
    # S is the strategy to evaluate
    S = strategy_dict['strategy']
    if player == pieces.kBlack:
        opponent = pieces.kWhite
    else:
        opponent = pieces.kBlack

    win_p = start_the_game(game, p_order, S, player, opponent, 0)

    if incomplete:
        print('Strategy incomplete')
    else:
        # report win probability for player p using strategy S
        print('Win probability for player {} (order {}): {}'.format(player, p_order, win_p))

if __name__ == '__main__':
    main()