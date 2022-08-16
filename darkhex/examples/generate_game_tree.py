from darkhex.algorithms.game_tree_generator import TreeGenerator
import darkhex.policy as policy


def main():
    policy_name = "4x3_handcrafted_second_player"
    policy_p0 = policy.SinglePlayerTabularPolicy(policy_name,
                                                 is_best_response=True)
    policy_p1 = policy.SinglePlayerTabularPolicy(policy_name)
    tree_generator = TreeGenerator(policy_p0, policy_p1, "best_responder",
                                   "handcrafted_player")


if __name__ == "__main__":
    main()
