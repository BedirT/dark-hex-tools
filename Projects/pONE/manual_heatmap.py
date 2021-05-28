# loads pickle data on given path
import argparse
from Projects.base.util import cPlot

parser = argparse.ArgumentParser()
parser.add_argument("--in_file", "-if", type=str,
                    help="File path to load the results from")
parser.add_argument("--out_file", "-f", type=str,
                    help="File path to save the results to")    
parser.add_argument("--target", "-t", type=str, default='B',
                    help="Parse for given sign. Choose from existing options please. ['W', 'B', '.', 't', 'T']. \
                    If multiple valid option add it as a string. i.e. 'WT'")          
parser.add_argument("--title", type=str, default='',
                    help="Title for the heatmap.")         
args = parser.parse_args()

p_names = [ 'first', 'second']
ks = ['B', 'W']
board_sizes = ['4x3', '3x3', '3x4']

for board_size in board_sizes:
    for p_name, k in zip(p_names, ks):
        args.in_file = 'Exp_Results/pONE/'+ board_size + '/'+ p_name +'Player.pkl'
        args.out_file = p_name +'_player_no-terminal' 
        args.targets =  [k + 'x']
        args.title = board_size + ' '+ p_name +' Player Without Terminal pONE Win States'

        cPlot.heat_map(args.in_file, args.out_file, args.targets, args.title)

        args.in_file = 'Exp_Results/pONE/'+ board_size + '/'+ p_name +'Player.pkl'
        args.out_file = p_name +'_player_terminal' 
        args.targets =  [k + 't']
        args.title = board_size + ' '+ p_name +' Player only Terminal pONE Win States'

        cPlot.heat_map(args.in_file, args.out_file, args.targets, args.title)

        args.in_file = 'Exp_Results/pONE/'+ board_size + '/'+ p_name +'Player.pkl'
        args.out_file = p_name +'_player_all' 
        args.targets =  [k + 'x', k + 't']
        args.title = board_size + ' '+ p_name +' Player All pONE Win States'

        cPlot.heat_map(args.in_file, args.out_file, args.targets, args.title)

# cPlot.heat_map(args.in_file, args.out_file, args.targets, args.title)        