# Just to see what we have as definite win moves
import pickle
from Projects.base.util.colors import colors, pieces
from Projects.base.util.print_tools import wrap_it
from Projects.base.game.hex import customBoard_print
from Projects.base.util.drive import missing_in_file

def glance(in_file=None, board_type=None):
    if board_type:
        in_file = missing_in_file(choice=board_type)
    else:
        if not in_file:
            in_file = missing_in_file()

    with open(in_file, 'rb') as f:
        dct = pickle.load(f)

    results = dct['results']
    num_cols = dct['num_cols'] 
    num_rows = dct['num_rows']
    num_of_moves = num_cols * num_rows

    while True:
        wrap_it('Printing the results given e and h. You can enter ctrl+d to get out at any time. Please enter e and h with a space in between (will print all results if -1 -1): ', colors.MIDTEXT, end=' ')
        try:
            e, h = map(int, input().strip().split(' '))
        except KeyboardInterrupt:
            exit()
        except:
            wrap_it('Invalid input please try again.', colors.WARNING)
            continue
        game_id = 0
        new_results = []
        if e == -1 and h == -1:
            for e in range(num_of_moves):
                for h in range(num_of_moves//2):
                    for res in results[e][h]:
                        if results[e][h][res] in [pieces.C_PLAYER1, pieces.C_PLAYER2]:
                            print(colors.UNDERLINE + str(game_id) + ' | Winner: ' + results[e][h][res] + colors.ENDC)
                            customBoard_print(res, num_cols, num_rows)
                            game_id+=1
                            new_results.append(res)
            break
        else:
            try:
                for res in results[e][h]:
                    if results[e][h][res] == 'B':
                        print(colors.UNDERLINE + str(game_id) + colors.ENDC)
                        customBoard_print(res, num_cols, num_rows)
                        game_id+=1
                        new_results.append(res)
                break
            except:
                print(colors.WARNING + 'Wrong e or h value entered. Try again.' + colors.ENDC)
    return new_results, h
        

    
