# loads pickle data on given path
import pickle
import pandas as pd
import numpy as np
import argparse
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import pandas as pd
import numpy as np

file_name = 'Results/PONE/3x3_pone.pkl'

with open(file_name, 'rb') as f:
    dct = pickle.load(f)

num_cols = dct['num_cols']
num_rows = dct['num_rows']
results = dct['results']

print(results)

all_total = 0
new_data_b = []
new_data_tot = []
y_size=range(len(results))
x_size=range(len(results[0]))
round_tot_b_h = [0] * len(results[0])
for e in y_size:
    round_tot_b = 0
    for h in x_size:
        tot_b = len([x for x in results[e][h] if results[e][h][x] != '='])
        tot = len([x for x in results[e][h]])
        new_data_b.append(tot_b)
        new_data_tot.append(tot)
        round_tot_b += tot_b
        round_tot_b_h[h] += tot_b
    new_data_b.append(round_tot_b)
    all_total += round_tot_b
round_tot_b_h.append(all_total)
new_data_b.extend(round_tot_b_h)

df = pd.DataFrame(np.array(new_data_b).reshape(len(results)+1, len(results[0])+1),
                  index=[*y_size, 'TOT'], columns=[*x_size, 'TOT'])

mask = np.zeros((len(results)+1, len(results[0])+1))
mask[:,-1] = True
mask[-1,:] = True

sns.heatmap(df, mask=mask, cmap='Blues')
sns.heatmap(df, alpha=0, cbar=False, annot=True, cmap='Blues', fmt='g', annot_kws={"size": 12, "color":"g"})

plt.show()

# inpe = 0
# while inpe != -1:
#     inpe, inph = map(int, input('Check for number of e and h: (input as - e h): ').strip().split(' '))
#     print('Number of Black win positions: ', ct_b[inpe][inph])
#     print('Number of total legal positions: ', ct_tot[inpe][inph])