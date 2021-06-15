'''
Sample runner for PONE.
'''
import argparse
from Projects.pONE.user_tools.trainer import train_pONE

parser = argparse.ArgumentParser()
parser.add_argument("--num_of_rows", "-nr", default=3, type=int,
                    help="Number of rows on the board.")
parser.add_argument("--num_of_cols", "-nc", default=3, type=int,
                    help="Number of columns on the board.")
parser.add_argument("--run_for_player", "-p", default='B', type=str,
                    help="The player to run the wins for.", choices=['W', 'B'])
parser.add_argument("--out_file", "-f", default="default_file", type=str,
                    help="File path to save the resulting list on. Please do not add any extension to file.\
                    here is an example usage:\n\t'filepath/filename'")  
args = parser.parse_args()

cs = [3]
rs = [3]
for c in cs:
    for r in rs:
        if c == 4 and r == 4:
            break
        train_pONE('firstPlayer', r, c, 'B')
        train_pONE('secondPlayer', r, c, 'W')

# train_pONE(args.out_file, args.num_of_rows, args.num_of_cols, args.run_for_player)