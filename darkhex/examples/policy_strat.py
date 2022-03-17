from darkhex.algorithms.policy_simplify import PolicySimplify
import pyspiel


def simplify_policy():
    game = pyspiel.load_game("dark_hex_ir(num_rows=2,num_cols=2,use_early_terminal=False)")
    ps = PolicySimplify(game, "....", 2, 2, 0)
    print(ps.info_states)


if __name__ == "__main__":
    simplify_policy()