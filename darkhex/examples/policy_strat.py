from darkhex.algorithms.policy_simplify import PolicySimplify
import pyspiel
import pickle


def simplify_policy(num_rows, num_cols, player, initial_board, policy_type='mccfr', include_isomorphic=True):
    game = pyspiel.load_game(f"dark_hex_ir(num_rows={num_rows},num_cols={num_cols},use_early_terminal=False)")
    ps = PolicySimplify(game, initial_board, num_rows, num_cols, player, policy_type, include_isomorphic)
    # print(ps.info_states)
    data = {
        "num_cols": num_cols,
        "num_rows": num_rows,
        "player": player,
        "isomorphic": include_isomorphic,
        "initial_board": initial_board,
        "strategy": ps.info_states,
    }
    with open(f"darkhex/data/simplified/{num_rows}x{num_cols}_p{player}.pkl", "wb") as f:
        pickle.dump(data, f)


if __name__ == "__main__":
    simplify_policy(3, 3, 0, ".........")