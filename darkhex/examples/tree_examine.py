"""
Sample file for using tree_run.py
"""
from darkhex.algorithms.tree_run import TreeRun


def main():
    file_name = "darkhex/data/strategy_data/4x3_mccfr/p1_2_0.04_0.01_25/"
    tree_run = TreeRun(file_name)
    tree_run.tree_run()


if __name__ == "__main__":
    main()
