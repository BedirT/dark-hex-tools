# loads pickle data on given path

import argparse
from Projects.pONE.user_tools.play import play_pONE

parser = argparse.ArgumentParser()
parser.add_argument("--in_file", "-if", type=str,
                    help="File path to load the results from")
args = parser.parse_args()

play_pONE(args.in_file)