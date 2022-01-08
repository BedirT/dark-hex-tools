import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import seaborn as sns
import pickle
from pathlib import Path

def heat_map(in_file, out_file, targets, title=None):
    with open(in_file, 'rb') as f:
        dct = pickle.load(f)

    results = dct['results']
    num_cols = dct['num_cols']
    num_rows = dct['num_rows']
    num_cells = num_rows * num_cols
    all_total = 0; new_data_b = []; new_data_tot = []
    e_size = num_cells + 1
    h_size = num_cells//2 + 1

    y_size=range(e_size)
    x_size=range(h_size)
    round_tot_b_h = [0] * h_size
    for e in y_size:
        round_tot_b = 0
        for h in x_size:
            tot_b = 0
            for x in results[e][h]:
                if results[e][h][x] in targets:
                    tot_b += 1
            tot = len([x for x in results[e][h]])
            new_data_b.append(tot_b)
            new_data_tot.append(tot)
            round_tot_b += tot_b
            round_tot_b_h[h] += tot_b
        new_data_b.append(round_tot_b)
        all_total += round_tot_b
    round_tot_b_h.append(all_total)
    new_data_b.extend(round_tot_b_h)

    df = pd.DataFrame(np.array(new_data_b).reshape(e_size+1, h_size+1),
                    index=[*y_size, 'TOT'], columns=[*x_size, 'TOT'])

    mask = np.zeros((e_size+1, h_size+1))
    mask[:,-1] = True
    mask[-1,:] = True
    plt.rc('axes', titlesize=15, labelsize=12)     # fontsize of the axes title
    
    ax = sns.heatmap(df, mask=mask, cmap='Blues')
    sns.heatmap(df, alpha=0, cbar=False, annot=True, cmap='Blues', 
                    fmt='g', annot_kws={"size": 10, "color":"xkcd:kelly green", "animated":True, "fontweight":"bold"}, ax = ax)
    title_prop = fm.FontProperties(fname="fonts/open-sans/OpenSans-Bold.ttf")
    subtext_prop = fm.FontProperties(fname="fonts/open-sans/OpenSans-Regular.ttf")

    if not title:
        title = 'For board size ' + str(num_rows) + 'x' + str(num_cols) + ' number of ' + str(targets) + "'s"
    plt.title(title, fontproperties=title_prop)
    plt.xlabel('Number of Hidden Stones', fontproperties=subtext_prop)
    plt.ylabel('Number of Empty cells', fontproperties=subtext_prop)
    
    find_piece = out_file.rfind('/')
    if find_piece != -1:
        folder_name = 'Visual/pONE/{}x{}/{}'.format(num_rows, 
            num_cols, out_file[:find_piece])
        file_name = out_file[out_file.rfind('/')+1:]
    else:
        folder_name = 'Visual/pONE/{}x{}'.format(num_rows, num_cols)
        file_name = out_file
    Path(folder_name).mkdir(parents=True, exist_ok=True)
    
    plt.savefig('{}/{}.png'.format(folder_name, file_name))
    
    plt.clf()