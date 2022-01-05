import sys
import argparse
sys.path.append('../../')
from Projects.SVerify.algorithms.tree_generator import tree_generator
from Projects.SVerify.algorithms.tree_run import tree_run
from Projects.SVerify.algorithms.lower_bound import LowerBoundCalculator

from Projects.SVerify.utils.util import choose_strategy

def main():
    # Get arguments from command line using argparse.
    parser = argparse.ArgumentParser()
    parser.add_argument('-tg', '--tree_generator', action='store_true', help='Generate tree.')
    parser.add_argument('-tr', '--tree_run', action='store_true', help='Run tree.')
    parser.add_argument('-lb', '--lower_bound', action='store_true', help='Calculate lower bound.')
    parser.add_argument('-cs', '--choose_strategy', action='store_true', help='Choose strategy.')
    # if cs is False then the following arguments are required
    parser.add_argument('-s', '--strategy', type=int, default='-1')
    args = parser.parse_args()

    if args.choose_strategy:
        game, file_name = choose_strategy()
    else:
        game, file_name = choose_strategy(choice=args.strategy)
    
    if args.lower_bound:
        lb = LowerBoundCalculator(game, file_name)
        lb.run()

    if args.tree_generator:
        try:
            tree_generator(game, file_name)
        except Exception as FileNotFoundError:
            print('File not found. Please run lower_bound first.')
    if args.tree_run:
        try:
            tree_run(file_name)
        except Exception as FileNotFoundError:
            print('File not found. Please run tree_generator first.')


if __name__ == '__main__':
    main()