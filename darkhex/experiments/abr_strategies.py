""" Get Approximate Best Response for a given strategy """
import pyspiel
import pickle

from open_spiel.python.algorithms.approximate_best_response_dqn import ApproximateBestResponseDQN

def get_abr(data_folder, eval_episodes, train_episodes):
    """ Returns the ABR for a given data folder. """
    with open(f"{data_folder}/game_info.pkl", "rb") as file:
        data = pickle.load(file)
    game = pyspiel.load_game("dark_hex_ir(num_rows=4,num_cols=3,use_early_terminal=True)")

    abr = ApproximateBestResponseDQN(game=game,
                                    eval_id=data["player"],
                                    eval_policy=data["strategy"],
                                    save_every=eval_episodes,
                                    num_train_episodes=train_episodes,
                                    eval_every=eval_episodes)
    val = (1 - (1 + abr.approximate_best_response()) / 2)
    # save the mean rewards
    return val


def main():
    """ Main function. """
    data_folder = "darkhex/data/strategy_data/4x3_mccfr/p1_4_0.1_0.0_0"
    eval_episodes = 1000
    train_episodes = 1000
    print(get_abr(data_folder, eval_episodes, train_episodes))


if __name__ == "__main__":
    main()