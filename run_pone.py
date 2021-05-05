import pickle
from PONE.pone import PONE

p = PONE([3,3])
chcc = [(x, p.state_results[x]) 
        for x in p.state_results if p.state_results[x] != '=']

with open('prob1_wins.pkl', 'wb') as f:
    pickle.dump(p.prob1_wins, f)

with open('all_non_B.pkl', 'wb') as f:
    pickle.dump(chcc, f)