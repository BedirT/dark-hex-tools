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
parser.add_argument("--out_file", "-f", default="default_file", type=str,
                    help="File path to save the resulting list on. Please do not add any extension to file.\
                    here is an example usage:\n\t'filepath/filename'")  
args = parser.parse_args()

train_pONE(args.out_file, args.num_of_rows, args.num_of_cols)