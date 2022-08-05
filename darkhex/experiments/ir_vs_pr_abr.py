""" Imperfect Recall vs Perfect Recall ABR experiment using
4x3 Dark Hex board with MCCFR. """
import pyspiel
import os
import matplotlib.pyplot as plt
import pickle
import tqdm

from open_spiel.python.algorithms.approximate_best_response_dqn import ApproximateBestResponseDQN


def compare_ir_pr(number_of_iterations, eval_freq, eval_episodes):
    num_rows = 4
    num_cols = 3
    game_pr = pyspiel.load_game("dark_hex(num_rows=4,num_cols=3)")
    game_ir = pyspiel.load_game("dark_hex_ir(num_rows=4,num_cols=3)")

    path = "tmp/experiments/ir_vs_pr_abr"
    # create folder if it doesn't exist
    if not os.path.exists(path):
        os.makedirs(path)

    solver_pr = pyspiel.OutcomeSamplingMCCFRSolver(game_pr)
    solver_ir = pyspiel.OutcomeSamplingMCCFRSolver(game_ir)
    evals = []
    for i in tqdm.tqdm(range(number_of_iterations)):
        solver_pr.run_iteration()
        solver_ir.run_iteration()
        if i % eval_freq == 0:
            policy_pr = solver_pr.average_policy()
            policy_ir = solver_ir.average_policy()
            _eval_pr = get_evaluation(game_pr, policy_pr, eval_episodes)
            _eval_ir = get_evaluation(game_ir, policy_ir, eval_episodes)
            print(f"Ep {i} PR: {_eval_pr} IR: {_eval_ir}")
            evals.append((_eval_pr, _eval_ir))

    # saving the results
    with open(f"{path}/solver_pr.pkl", "wb") as file:
        pickle.dump(solver_pr, file)
    with open(f"{path}/solver_ir.pkl", "wb") as file:
        pickle.dump(solver_ir, file)
    with open(f"{path}/eval.pkl", "wb") as file:
        pickle.dump(evals, file, pickle.HIGHEST_PROTOCOL)

    # plotting the evals
    plt.plot(evals)
    plt.xlabel(f"Iterations x{eval_freq}")
    plt.ylabel("Approximate Exploitability")
    plt.savefig(f"{path}/eval.png")
    plt.show()


def get_evaluation(game, policy, eval_episodes):
    """ Returns the evaluation of the policy. """
    abr = ApproximateBestResponseDQN(game,
                                     0,
                                     policy,
                                     save_every=eval_episodes,
                                     num_train_episodes=eval_episodes)
    p0_res = abr.approximate_best_response()
    abr = ApproximateBestResponseDQN(game,
                                     1,
                                     policy,
                                     save_every=eval_episodes,
                                     num_train_episodes=eval_episodes)
    p1_res = abr.approximate_best_response()
    return get_prob_value(p0_res), get_prob_value(p1_res)


def get_prob_value(x):
    return (1 - (1 + x) / 2)


def main():
    """ Main function. """
    compare_ir_pr(number_of_iterations=1000, eval_freq=10, eval_episodes=100000)


if __name__ == "__main__":
    main()
