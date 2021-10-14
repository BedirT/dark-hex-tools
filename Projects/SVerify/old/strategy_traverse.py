'''
Given the strategy, traverse the strategy tree and 
return to the dictionary of information states with
the corresponding moves (following the strategy).

Opponent plays every valid move, while player plays
accordingly to the strategy. If the strategy is not
complete (i.e. there are still states that are not
explored), then the strategy is not valid.
'''
from collections import defaultdict
from Projects.base.game.darkHex import DarkHex
from Projects.base.game.hex import pieces

def update_history(hist, action, res):
    '''
    Update the history of the game.
    '''
    if res == pieces.kFail:
        return hist + str(action) + 'f'
    else:
        return hist + str(action) + 's'

def rewind_history(hist):
    '''
    Rewind the game.
    '''
    if len(hist) > 0:
        return hist[:-2]
    else:
        return hist

def traverseStrategy(game, hist, strategy, player, information_states):
    '''
    Traverse the strategy tree and return
    the dictionary of information states with
    the corresponding moves (following the strategy).

    There are two players:
        - player_o: the opponent
        - player: the player
        (player_o plays every valid move, while player
        plays accordingly to the strategy)
    
    This function will be called recursively, playing
    the game until every possible information state
    is explored.

    This is a recursive function.

    Updates the information_states dictionary with the 
    information state as the key and the corresponding
    moves as the value (as a list with the probability
    of choosing said action, i.e. if there are two moves
    then the probability of choosing the first move is
    0.5)
    '''
    player_o = game.rev_color[player]
    if game.turn_information_func() == player:
        # players turn
        for action in strategy[hist]:
            info_state = game.get_information_set(player)
            _, res, _ = game.step(player, action)
            # adding action to the set
            information_states[info_state].add(action)
            if res == player:
                # player wins
                # rewind the game
                game.rewind()
                # strategy.rewind()
                return
            else:
                # continue playing the game
                hist = update_history(hist, action, res)
                traverseStrategy(game, hist, strategy, player, information_states)
                hist = rewind_history(hist)
                # rewind the game
                game.rewind()
                # strategy.rewind()
    else:
        # opponents turn
        for action in game.valid_moves:
            _, res, _ = game.step(player_o, action)
            if res == player_o:
                # o wins
                game.rewind()
                return 0
            else:
                # continue playing the game
                traverseStrategy(game, hist, strategy, player, information_states)
                # rewind the game
                game.rewind()
    
def strategyTraverse(player):
    '''
    player is either pieces.kBlack or pieces.kWhite
    Main function;
        - Create the strategy for player 0/1 using the
          ActionNode class. 
        - Create the game for players to play on.
        - Traverse the strategy tree and return
          the dictionary of information states with
          the corresponding moves (following the strategy).
    '''
    # Create the strategy using the ActionNode class.
    # strategy = createStrategy()
    strategy = {
        '': [2, 1],
        '2s': [0, 1],
        '2s0f': [1],
        '2s1f': [0],
        '1s': [2, 3],
        '1s2f': [3],
        '1s3f': [2],
    }
    board_size = [2,2]
    game = DarkHex(BOARD_SIZE=board_size,
                    verbose=False)
    hist = '' # starting point for action selection
    information_states = defaultdict(lambda:set())
    traverseStrategy(game, hist, strategy, player, information_states)

    # convert the action set to a list of tuples with the action and
    # probability of choosing said action
    for info_state in information_states:
        actions = list(information_states[info_state])
        num_actions = len(actions)
        information_states[info_state] = [(action, 1/num_actions) for action in actions]

    return information_states
    
the_dict = strategyTraverse(pieces.kBlack)
for key in the_dict:
    print('"'+ key + '":', the_dict[key], end=',\n')