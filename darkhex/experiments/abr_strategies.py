""" Get Approximate Best Response for a given strategy """
import pyspiel
import pickle

from open_spiel.python.algorithms.approximate_best_response_dqn import ApproximateBestResponseDQN

def get_abr(data_folder, eval_episodes, train_episodes, save_path):
    """ Returns the ABR for a given data folder. """
    with open(f"{data_folder}/game_info.pkl", "rb") as file:
        data = pickle.load(file)
    game_str = "dark_hex_ir(num_rows=4,num_cols=3,use_early_terminal=True)"

    abr = ApproximateBestResponseDQN(game=game_str,
                                    eval_id=data["player"],
                                    eval_policy=data["strategy"],
                                    save_every=train_episodes,
                                    num_train_episodes=train_episodes,
                                    eval_every=train_episodes/10,
                                    num_eval_games=eval_episodes,
                                    checkpoint_dir="tmp/"+save_path)
    val = (abr.approximate_best_response() + 1) / 2
    # save the mean rewards
    return val


def main():
    """ Main function. """
    data_path = "p1_6_0.1_0.0_0"
    data_folder = "darkhex/data/strategy_data/4x3_mccfr/" + data_path
    eval_episodes = int(1e4)
    train_episodes = int(1e6)
    abr_res = get_abr(data_folder, eval_episodes, train_episodes, data_path)
    print(abr_res)
    # write abr results on a text file
    with open(f"{data_folder}/abr.txt", "w") as file:
        file.write(f"Number of train episodes: {train_episodes}\n")
        file.write(f"Number of eval episodes: {eval_episodes}\n")
        file.write("Approximate Exploitability: " + str(abr_res))
            


if __name__ == "__main__":
    main()