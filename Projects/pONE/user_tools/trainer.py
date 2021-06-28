import pickle
from pathlib import Path

from Projects.pONE.pONE import pONE

def train_pONE(out_file, rows, cols, visible_player):
    p = pONE([rows, cols], visible_player)
    p.keep_non_neutrals()
    print(len(p.prob1_wins[8][0]))
    exit()
    
    dct = {
            'results': p.prob1_wins,
            'num_cols': cols,
            'num_rows': rows,
            'visible_player': p.vis_p,
            'hidden_player': p.hid_p
        }
        
    find_piece = out_file.rfind('/')
    if find_piece != -1:
        folder_name = 'Exp_Results/pONE/{}x{}/{}'.format(rows, 
            cols, out_file[:find_piece])
        file_name = out_file[out_file.rfind('/')+1:]
    else:
        folder_name = 'Exp_Results/pONE/{}x{}'.format(rows, cols)
        file_name = out_file
    Path(folder_name).mkdir(parents=True, exist_ok=True)
    if not file_name:
        file_name = 'no_name'
    with open('{}/{}.pkl'.format(folder_name, file_name), 'wb') as f:
        pickle.dump(dct, f)