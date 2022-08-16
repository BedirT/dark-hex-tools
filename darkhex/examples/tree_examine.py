"""
Sample file for using tree_run.py
"""
from darkhex.algorithms.game_tree_examiner import GameTreeRunner


def tree_examine():
    tree_name = "best_responder-handcrafted_player"
    tree_run = GameTreeRunner(tree_name)
    tree_run.tree_run()


if __name__ == "__main__":
    tree_examine()
