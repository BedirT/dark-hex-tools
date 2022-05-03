from darkhex.utils.util import save_file, load_file, convert_to_infostate, game_over
import pandas as pd

def main():
    folder = "darkhex/data/definite_wins/4x3"
    data = load_file(f"{folder}/results_w_p.pkl")

    new_data = []
    for player in range(2):
        for h, p_data in enumerate(data[player]):
            for board, res in p_data.items():
                info_state = convert_to_infostate(board, 2, 2, player)
                if not game_over(info_state):
                    print(f"{info_state} {res}")
                    new_data.append((info_state, res))
    # dont add the header to the csv
    df = pd.DataFrame(new_data, columns=["info_state", "res"])
    df.to_csv(f"{folder}/results_w_p.csv", index=False, header=False)

if __name__ == "__main__":
    main()