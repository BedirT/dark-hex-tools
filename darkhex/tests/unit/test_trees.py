import pytest
from darkhex.algorithms.game_tree_generator import TreeGenerator
import darkhex.policy as policy
import os


def test_tree_generator():
    file_path = "4x3_handcrafted_second_player"
    policy_p0 = policy.SinglePlayerTabularPolicy(file_path,
                                                 is_best_response=True)
    policy_p1 = policy.SinglePlayerTabularPolicy(file_path)
    tree_generator = TreeGenerator(policy_p0, policy_p1, "test0", "test1")
    assert os.path.exists("darkhex/data/game_trees/test0-test1/tree.dot")
    assert os.path.exists("darkhex/data/game_trees/test0-test1/tree.svg")
    assert os.path.exists("darkhex/data/game_trees/test0-test1/tree.pdf")
    os.system("rm -rf darkhex/data/game_trees/test0-test1")


def test_tree_examiner():
    file_path = "4x3_handcrafted_second_player"
    policy_p0 = policy.SinglePlayerTabularPolicy(file_path,
                                                 is_best_response=True)
    policy_p1 = policy.SinglePlayerTabularPolicy(file_path)
    tree_generator = TreeGenerator(policy_p0, policy_p1, "test0", "test1")
    tree_name = "test0-test1"
    tree_run = GameTreeRunner(tree_name)
    os.system("rm -rf darkhex/data/game_trees/test0-test1")
