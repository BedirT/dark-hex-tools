# loads pickle data on given path
import pickle

file_name = 'prob1_state_res.pkl'

with open(file_name, 'rb') as f:
    a = pickle.load(f)

for i in a:
    print(i)