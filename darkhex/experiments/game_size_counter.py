""" Counts the number of histories in a game. """
import pyspiel


class CountHistories:

    def __init__(self, game: pyspiel.Game) -> None:
        """Counts the number of histories in a game."""
        state = game.new_initial_state()
        print("Counting histories...\nNumber of Non Terminal\tNumber of Terminal")
        self.num_non_terminal = 0
        self.num_terminal = 0
        self._count_histories(state)

    def _count_histories(self, state: pyspiel.State) -> None:
        """Counts the number of histories in a game."""
        if state.is_terminal():
            self.num_terminal += 1
            self.report()
            return
        self.num_non_terminal += 1
        self.report()
        for action in state.legal_actions():
            new_state = state.child(action)
            self._count_histories(new_state)
            
    def report(self) -> None:
        """Prints the number of histories in a game."""
        red, green, end = "\033[91m", "\033[92m", "\033[0m"
        print(f"{red}{self.num_non_terminal}{end}\t{green}{self.num_terminal}{end}", end="\r")

def main():
    """Main function."""
    game = pyspiel.load_game("dark_hex(num_rows=3,num_cols=3)")
    count_histories = CountHistories(game)
    print("Non-terminal histories: {}".format(count_histories.num_non_terminal))
    print("Terminal histories: {}".format(count_histories.num_terminal))


if __name__ == "__main__":
    main()
