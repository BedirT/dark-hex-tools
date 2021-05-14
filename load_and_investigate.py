# loads pickle data on given path
import pickle
import pandas as pd
import numpy as np

file_name = 'Exp_Results/4x3_pone_dp.pkl'

with open(file_name, 'rb') as f:
    a = pickle.load(f)

ct_tot = [[0 for _ in range(7)] for _ in range(12)]
ct_b = [[0 for _ in range(7)] for _ in range(12)]

all_total = 0
new_data_b = []
new_data_tot = []
y_size=range(len(a))
x_size=range(len(a[0]))
round_tot_b_h = [0] * len(a[0])
for e in y_size:
    round_tot_b = 0
    for h in x_size:
        tot_b = len([x for x in a[e][h] if a[e][h][x] != '='])
        tot = len([x for x in a[e][h]])
        new_data_b.append(tot_b)
        new_data_tot.append(tot)
        round_tot_b += tot_b
        round_tot_b_h[h] += tot_b
    new_data_b.append(round_tot_b)
    all_total += round_tot_b
round_tot_b_h.append(all_total)
new_data_b.extend(round_tot_b_h)

df = pd.DataFrame(np.array(new_data_b).reshape(len(a)+1, len(a[0])+1),
                  index=[*y_size, 'TOT'], columns=[*x_size, 'TOT'])

import seaborn as sns
cm = sns.light_palette("blue", as_cmap=True)
s = df.style.background_gradient(cmap=cm)
s

# inpe = 0
# while inpe != -1:
#     inpe, inph = map(int, input('Check for number of e and h: (input as - e h): ').strip().split(' '))
#     print('Number of Black win positions: ', ct_b[inpe][inph])
#     print('Number of total legal positions: ', ct_tot[inpe][inph])