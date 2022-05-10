import pyspiel
import az_br.ismcts as ismcts
import az_br.utils as utils
import numpy as np

p_color = '\033[38;2;46;201;62m'
o_color = '\033[38;2;194;62;62m'
neutral_color = '\033[38;2;255;255;255m'
end_color = '\033[0m'
bar_size = 50
bar_indicator = '\u25AC'
neutral_indicator = '\u25C9'


def test_so_ismcts_pom():
    obs_player = 0
    n_games = 1000
    args = utils.dotdict(
        num_simulations=2000,
        k=1.41,  # optimal exploration factor for kuhn poker 1.41
        branching_factor=-1,
    )
    game = pyspiel.load_game("kuhn_poker")
    ismcts_pom = ismcts.ISMCTS(game, obs_player, args)
    # play against random
    chips_per_hand = [0, 0]  # p, o
    num_wins = [0, 0]  # p, o
    for n in range(n_games):
        np.random.seed(n)
        state = game.new_initial_state()
        while not state.is_terminal():
            if state.current_player() == obs_player:
                a = ismcts_pom.run(state)
            else:
                a = np.random.choice(state.legal_actions())
            state = state.child(a)
        if state.returns()[obs_player] > 0:
            num_wins[0] += 1
        else:
            num_wins[1] += 1
        chips_per_hand[0] += state.returns()[obs_player]
        chips_per_hand[1] += state.returns()[1 - obs_player]

        o_win_str = bar_indicator * (bar_size * num_wins[1] //
                                     (num_wins[1] + num_wins[0]))
        p_win_str = bar_indicator * (bar_size - len(o_win_str))
        print(
            f'{n+1}/{n_games}:' + ' ' * 10 +
            f'ISMCTS {chips_per_hand[0]}|{num_wins[0]} |{p_color}{p_win_str}{end_color}'
            + f'{neutral_color}{neutral_indicator}{end_color}' +
            f'{o_color}{o_win_str}{end_color}| {num_wins[1]}|{chips_per_hand[1]} Random Player',
            end="\r",
            flush=True)
    print()


if __name__ == '__main__':
    test_so_ismcts_pom()
