from collections import defaultdict
from Projects.base.game.darkHex import DarkHex
from Projects.base.game.hex import print_init_board, pieces

num_cols = 4
num_rows = 3

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

infoset_to_action_p1 = defaultdict(set)
infoset_to_action_p2 = defaultdict(set)
save_ls = []
while True:
    # if the game is over, invalid if chose to move
    if human_like:
        p_action = input("Play 0-1 for indicating the player and then action/or just '-' for rewind/'x' to exit: ").strip().split(' ')
        moves.append(p_action)
        save_ls.append(p_action)
    else:
        # take the next action from the input file
        p_action = moves.pop(0)
    if p_action[0] == 'x':
        break
    elif p_action[0] == '-':
        game.rewind()
        if human_like:
            game.printBoard()
            print(game.valid_moves_colors[pieces.kBlack], game.hidden_stones_count(pieces.kBlack), p_action[0])
            print(game.valid_moves_colors[pieces.kWhite], game.hidden_stones_count(pieces.kWhite), p_action[0])
        continue
    elif p_action[0] == '1':
        player = pieces.kBlack
    elif p_action[0] == '0':
        player = pieces.kWhite
    else:
        # p_action is invalid
        game.verbose = True
        print("Invalid action {} / {}".format(p_action, result))
        game.printBoard()
        print(game.valid_moves_colors[pieces.kBlack])
        print(game.valid_moves_colors[pieces.kWhite])
        if human_like:
            game.verbose = True
            continue
        print(moves)
        exit()
    prev_infoset = game.get_information_set(player)
    action = int(p_action[1])
    # step the game
    _, result, _ = game.step(player, action)
    if player == pieces.kBlack:
        infoset_to_action_p1[prev_infoset].add(action)
    if player == pieces.kWhite:
        infoset_to_action_p2[prev_infoset].add(action)
    # print infoset for player1 and player2
    if human_like:
        # print the board
        game.printBoard()
        print("Player B infoset:", game.get_information_set(pieces.kBlack))
        print("Player W infoset:", game.get_information_set(pieces.kWhite))
        print("BOARD:", game.BOARD)

# print infosets in a file
# seperate infosets by a new line get it in quatation marks
# put actions in between brackets and add their probabilities
# next to them and seperate them by a comma.
# for example:
# "infoset": [(0, 0.5), (1, 0.5)]
# or if it was 3 actions:
# "infoset": [(0, 0.33), (1, 0.33), (3, 0.34)]

# which players policy to save.
# 0 for player1 and 1 for player2
# if you want to save both players policies, put 0 and 1
p_save = input("Which players policy to save? (0 or 1, 01 for both): ").strip()
with open("Projects/SVerify/output.txt", "w") as f:
    if '0' in p_save:
        for infoset, actions in infoset_to_action_p1.items():
            f.write("\"{}\": [".format(infoset))
            for idx, action in enumerate(actions):
                div = round(1/len(actions), 2)
                if idx == len(actions)-1 and \
                    round(1/len(actions),2)*len(actions) != 1/len(actions)*len(actions):
                    # last action
                    div = round(1 - (round(1/len(actions),2) * (len(actions)-1)),2)
                f.write("({}, {}),".format(action, div))
            f.write("],\n")
    f.write("\n\n")
    if '1' in p_save:
        for infoset, actions in infoset_to_action_p2.items():
            f.write("\"{}\": [".format(infoset))
            for action in actions:
                f.write("({}, {}),".format(action, 1/len(actions)))
            f.write("],\n")

# save the inputs given by the user in a file
with open("Projects/SVerify/input.txt", "w") as f:
    for move in save_ls:
        f.write(" ".join(move) + "\n")