from collections import defaultdict
from Projects.base.game.darkHex import DarkHex
from Projects.base.game.hex import print_init_board, pieces

num_cols = 2
num_rows = 2

def infoset(board, hidden_stones, player) -> str:
    """
    Returns the infoset of the current board.
    """
    s = 'P' + str(player) + ' '
    for i in range(len(board)):
        s += str(board[i])
    s += str(hidden_stones)
    return s

game = DarkHex(BOARD_SIZE=[num_rows, num_cols])
result = pieces.kDraw

# if human_like is True then the input will be given at each play
# and the game will not be played from the input file
# if human_like is False then the game will be played from the input file
human_like = True

moves = []
# read the input file if human_like is False
if not human_like:
    game.verbose=False
    # input.txt is the file that contains the moves of the game
    # the moves are separated by next line
    with open("Projects/input.txt", "r") as f:
        moves = f.read().split("\n")
        # make it a list of moves
        moves = [move.split(" ") for move in moves]

# print(moves)
# exit()
if human_like:
    print_init_board(num_cols=game.num_cols, num_rows=game.num_rows)

infoset_to_action = defaultdict(set)
results = []
playernum = 0
while True:
    # if the game is over, invalid if chose to move
    if human_like:
        p_action = input("Play 0-1 for indicating the player and then action/or just '-' for rewind/'x' to exit: ").strip().split(' ')
        moves.append(p_action)
    else:
        # take the next action from the input file
        p_action = moves.pop(0)
    prev_infoset = infoset(game.BOARDS[pieces.kBlack], game.hidden_stones_count(pieces.kBlack), playernum)
    if p_action[0] == 'x':
        break
    elif p_action[0] == '-':
        result = results.pop()
        game.rewind(result == pieces.kFail)
        if human_like:
            game.printBoard()
            print(game.valid_moves_colors[pieces.kBlack], game.hidden_stones_count(pieces.kBlack), playernum)
            print(game.valid_moves_colors[pieces.kWhite], game.hidden_stones_count(pieces.kWhite), playernum)
        continue
    elif p_action[0] == '0' and result in [pieces.kDraw, pieces.kFail]:
        player = pieces.kBlack
    elif p_action[0] == '1' and result in [pieces.kDraw, pieces.kFail]:
        player = pieces.kWhite
    else:
        # p_action is invalid
        game.verbose = True
        print("Invalid action {} / {}".format(p_action, result))
        game.printBoard()
        print(game.valid_moves_colors[pieces.kBlack])
        print(game.valid_moves_colors[pieces.kWhite])
        playernum = (playernum + 1) % 2
        if human_like:
            game.verbose = False
            continue
        print(moves)
        exit()
    action = int(p_action[1])
    # step the game
    board, result, reward = game.step(player, int(action))
    if player == pieces.kBlack:
        infoset_to_action[prev_infoset].add(action)
    # print infoset for player1 and player2
    if human_like:
        # print the board
        game.printBoard()
        print("Player 1 infoset:", infoset(game.BOARDS[pieces.kBlack], game.hidden_stones_count(pieces.kBlack), playernum))
        print("Player 2 infoset:", infoset(game.BOARDS[pieces.kWhite], game.hidden_stones_count(pieces.kWhite), playernum))
    results.append(result)

# print infosets in a file
# seperate infosets by a new line get it in quatation marks
# put actions in between brackets and add their probabilities
# next to them and seperate them by a comma.
# for example:
# "infoset": [(0, 0.5), (1, 0.5)]
# or if it was 3 actions:
# "infoset": [(0, 0.33), (1, 0.33), (3, 0.34)]
print(infoset_to_action)
with open("Projects/output.txt", "w") as f:
    for infoset, actions in infoset_to_action.items():
        # legal actions are from infoset
        # if infoset cell is '.' then its legal
        legal_actions = [idx-3 for idx,cell in enumerate(infoset) if cell == '.']
        f.write("\"{}\": [".format(infoset))
        for action in actions:
            f.write("({}, {}),".format(action, 1/len(actions)))
        for action in legal_actions:
            if action not in actions:
                f.write("({}, {}),".format(action, 0))
        f.write("],")
        f.write("\n")

# save the inputs given by the user in a file
# with open("Projects/input.txt", "w") as f:
#     for move in moves:
#         f.write(" ".join(move) + "\n")