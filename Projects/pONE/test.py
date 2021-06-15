import pickle 

file_name = 'Exp_Results/pONE/3x3/firstPlayer.pkl'

with open(file_name, 'rb') as f:
    dct = pickle.load(f)

results = dct['results']
num_cols = dct['num_cols']
num_rows = dct['num_rows']

nc = num_cols*num_rows

for e in range(nc+1):
    for h in range((nc+1)//2):
        for x in results[e][h]:
            if e == 8:
                print(results[e][h][x], x)
            if results[e][h][x][0] != '=' and h == 0 and e == 9:
                print(x, h)



# def player_play(e, h, results, game_board):
    # res = game_board
    # for mv in range(len(game_board)):
    #     if game_board[mv] == '.':
    #         res[mv] = 'B'
    #         if tuple(res) in results[e-1][h] and \
    #             results[e-1][h][tuple(res)][0] == 'B':
    #             return mv
    #         res[mv] = '.'

# print(player_play(9, 0, results, ['.']*9))