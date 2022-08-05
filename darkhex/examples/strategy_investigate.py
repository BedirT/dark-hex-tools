""" Loads and lets you investigate a strategy. """
import pyspiel
import pickle
import os

# def investigate(data_path):
#     """ Loads a strategy and lets you investigate it. """
#     with open(data_path, "rb") as f:
#         data = pickle.load(f)
#     strategy = data["strategy"]
#     game = pyspiel.load_game("dark_hex_ir(num_rows=4,num_cols=3)")
#     state = game.new_initial_state()
#     h = []
#     while True:
#         if state.is_terminal():
#             print(f"Terminal state: {state.returns()}")
#             inp = input("b to go back a step, r to restart, q to quit")
#             if inp == "b":
#                 state = h[-1]
#                 h = h[:-1]
#             elif inp == "r":
#                 state = game.new_initial_state()
#                 h = []
#             elif inp == "q":
#                 break
#         elif state.current_player() == data["player"]:
#             print(f"Current state: {state.information_state_string()}")
#             print(f"State policy: {strategy[state.information_state_string()]}")
#             action = input("Pick a branch to continue: (Strategy will take this action)")
#             new_state = state.child(int(action))
#             h.append(state)
#             state = new_state
#         else:
#             pass
def write_to_file(data_path):
    """ Writes a strategy to a file. """
    game_info_path = data_path + "/game_info.pkl"
    if not os.path.exists(game_info_path):
        print(f"No game info found at {game_info_path}")
        return
    with open(game_info_path, "rb") as f:
        data = pickle.load(f)
    strategy = data["strategy"]
    with open(data_path + "/strategy.txt", "w") as f:
        for key, value in strategy.items():
            f.write(f"{key} {value}\n")


def write_to_file_all_folders(data_path):
    """ Writes a strategy to all folders in the given folder. """
    for folder in os.listdir(data_path):
        if os.path.isdir(os.path.join(data_path, folder)):
            print(f"Writing to path {os.path.join(data_path, folder)}/strategy.txt")
            write_to_file(str(os.path.join(data_path, folder)))



if __name__ == "__main__":
    data_path = "darkhex/data/strategy_data/4x3_mccfr"
    write_to_file_all_folders(data_path)