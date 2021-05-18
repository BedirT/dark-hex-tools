'''
Sample runner for PONE.
'''
import pickle
from Projects.pONE.pONE import pONE
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--num_of_rows", "-nr", default=3, type=int,
                    help="Number of rows on the board.")
parser.add_argument("--num_of_cols", "-nc", default=3, type=int,
                    help="Number of columns on the board.")
parser.add_argument("--out_file", "-f", default="default_file", type=str,
                    help="File path to save the resulting list on. Please do not add any extension to file.\
                    here is an example usage:\n\t'filepath/filename'")  
args = parser.parse_args()

p = pONE([args.num_of_rows, args.num_of_cols])

dct = {
        'results': p.state_results,
        'num_cols': args.num_of_cols,
        'num_rows': args.num_of_rows
      }
find_piece = args.out_file.rfind('/')
if find_piece != -1:
    folder_name = 'Exp_Results/pONE/{}x{}/{}'.format(args.num_of_rows, 
        args.num_of_cols, args.out_file[:find_piece])
    file_name = args.out_file[args.out_file.rfind('/')+1:]
else:
    folder_name = 'Exp_Results/pONE/{}x{}'.format(args.num_of_rows, args.num_of_cols)
    file_name = args.out_file
Path(folder_name).mkdir(parents=True, exist_ok=True)
with open('{}/{}.pkl'.format(folder_name, file_name), 'wb') as f:
    pickle.dump(dct, f)