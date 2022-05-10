"""Strategy generator app with Tkinter GUI."""
import math
import os
import tkinter as tk
import typing
from collections import Counter
from copy import deepcopy
from tkinter import Grid, filedialog, font, messagebox

from darkhex.utils.cell_state import cellState
from darkhex.utils.isomorphic import isomorphic_single
from darkhex.utils.util import num_action, save_file, updated_board, load_file, convert_to_xo


class gameBuffer:
    """History buffer for the game to use for rewind and restart."""

    def __init__(self, initial_board: str, num_rows: int, num_cols: int,
                 player: int, include_isomorphic: bool, stratgen_class) -> None:
        self.game_info = {
            "num_rows": num_rows,
            "num_cols": num_cols,
            "player": player,
            "isomorphic": include_isomorphic,
            "initial_board": initial_board,
        }
        self.info_states = []
        self.moves_and_boards = []
        self.board = []
        self.move_stack = []
        self.given_inputs = []
        self.stratgen_class = stratgen_class
        self.add_history_buffer(stratgen_class)

    def add_history_buffer(self, stratgen_class, given_input=None):
        self.info_states.append(deepcopy(stratgen_class.info_states))
        self.moves_and_boards.append(deepcopy(stratgen_class.moves_and_boards))
        self.board.append(deepcopy(stratgen_class.board))
        self.move_stack.append(deepcopy(stratgen_class.move_stack))
        if given_input:
            self.given_inputs.append(given_input)

    def rewind(self) -> str:
        """Rewinds the game."""
        if len(self.info_states) > 1:
            self.info_states.pop()
            self.moves_and_boards.pop()
            self.board.pop()
            self.move_stack.pop()
            self.given_inputs.pop()
        else:
            return "Cannot rewind anymore.\n"
        self._update_game(-1)
        return "Rewinded to the previous state.\n"

    def restart(self) -> str:
        """Restarts the game."""
        self.info_states = self.info_states[:1]
        self.moves_and_boards = self.moves_and_boards[:1]
        self.board = self.board[:1]
        self.move_stack = self.move_stack[:1]
        self.given_inputs = []
        self._update_game(0)
        return "Restarted the game.\n"

    def search_history(self, info_state):
        """Search the history buffer for the given info state."""
        for idx, board in enumerate(self.board):
            if board == info_state:
                return idx
        return -1

    def _revert(self, idx):
        self.info_states = self.info_states[:idx + 1]
        self.moves_and_boards = self.moves_and_boards[:idx + 1]
        self.board = self.board[:idx + 1]
        self.move_stack = self.move_stack[:idx + 1]
        self.given_inputs = self.given_inputs[:idx + 1]
        self._update_game(idx)

    def _update_game(self, idx):
        self.stratgen_class.info_states = deepcopy(self.info_states[idx])
        self.stratgen_class.moves_and_boards = deepcopy(
            self.moves_and_boards[idx])
        self.stratgen_class.board = deepcopy(self.board[idx])
        self.stratgen_class.move_stack = deepcopy(self.move_stack[idx])

    def revert_to_state(self, idx=None, state=None):
        if idx and state:
            raise ValueError("Cannot use both idx and state.")
        if idx:
            self._revert(idx)
        elif state:
            idx = self.search_history(state)
            if idx != -1:
                self._revert(idx)
            else:
                raise ValueError("State not found.")


colors = {
    "black": "#000000",
    "white": "#ffffff",
    ".": "#bd6966",
    "x": "#2b2222",
    "o": "#c7b6a3",
    "btn_txt": "#9bbede",
    "btn_bg": "#06192b",
}


class StrategyGeneratorGUI:

    def __init__(
        self,
        initial_board: str,
        num_rows: int,
        num_cols: int,
        player: int,
        include_isomorphic: bool = True,
        cell_edge_length: int = 70,
    ) -> None:
        self.root = tk.Tk()
        # Set the title of the window.
        self.root.title("Strategy Generator")

        self.len_ce = cell_edge_length
        self.r = self.len_ce // 2

        # Set the window unresizable.
        self.root.resizable(False, False)

        # Configure the row and columns
        Grid.rowconfigure(self.root, 0, weight=1)
        Grid.columnconfigure(self.root, 0, weight=1)

        self._setup_game(initial_board, num_rows, num_cols, player,
                         include_isomorphic)

        self.root.mainloop()

    def _setup_game(self, initial_board, nr, nc, player,
                    include_isomorphic) -> None:
        self.nr = nr
        self.nc = nc
        self.player = player
        self.include_isomorphic = include_isomorphic
        self.initial_board = initial_board

        self.frm_board = self._init_board_frame()
        self.frm_board.grid(row=0, column=0, sticky="nsew")

        self.draw_board(initial_board)

        self.frm_menu_bar = self._init_menu_frame()
        self.frm_menu_bar.grid(row=1, column=0, sticky="nsew")

        self.frm_input_bar = self._init_input_frame()
        self.frm_input_bar.grid(row=2, column=0, sticky="nsew")

        self.frm_log_bar = self._init_log_frame()
        self.frm_log_bar.grid(row=3, column=0, sticky="nsew")

        # menu bar
        self.menu = self._init_menu()
        self.root.config(menu=self.menu)

        self.strat_gen = StrategyGenerator(initial_board, self.nr, self.nc,
                                           player, include_isomorphic)

    def _init_menu_frame(self) -> tk.Frame:
        frm = tk.Frame(padx=10, pady=10)

        # Add a button to the frame
        btn_rewind = tk.Button(frm,
                               text="Rewind",
                               command=self.rewind,
                               height=2,
                               font="Helvetica 14 bold")
        btn_restart = tk.Button(
            frm,
            text="Restart",
            command=self.restart,
            height=2,
            font="Helvetica 14 bold",
        )
        btn_rewind.grid(row=0, column=0, sticky="nsew")
        btn_restart.grid(row=0, column=1, sticky="nsew")
        Grid.columnconfigure(frm, 0, weight=1)
        Grid.columnconfigure(frm, 1, weight=1)

        return frm

    def _init_input_frame(self) -> tk.Frame:
        frm = tk.Frame(padx=10, pady=10)

        # Add a label to the frame
        lbl_input = tk.Label(frm, text="Input:", font="Helvetica 14 bold")
        lbl_input.grid(row=0, column=0, sticky="nsew")
        # Input field.
        self.ent_input = tk.Entry(frm, font="Helvetica 14")
        self.ent_input.grid(row=0, column=1, sticky="nsew")

        btn_random = tk.Button(
            frm,
            text="Random",
            command=self.random_input,
            height=2,
            font="Helvetica 14 bold",
        )

        # Add a button to the frame
        btn_submit = tk.Button(
            frm,
            text="Enter",
            command=self.enter,
            height=2,
            font="Helvetica 14 bold",
            padx=20,
        )
        # also run self.enter if the enter key is pressed
        self.ent_input.bind("<Return>", lambda event: self.enter())

        btn_submit.grid(row=0, column=2, sticky="e")
        btn_random.grid(row=0, column=3, sticky="e")

        Grid.columnconfigure(frm, 0, weight=1)
        Grid.columnconfigure(frm, 1, weight=7)
        Grid.columnconfigure(frm, 2, weight=1)
        Grid.columnconfigure(frm, 3, weight=1)

        Grid.rowconfigure(frm, 0, weight=1)

        return frm

    def _init_board_frame(self) -> tk.Frame:
        self.loc_cen = [(0, 0) for _ in range(self.nr * self.nc)]
        self.coord_cells = [
            (0 for __ in range(6)) for _ in range(self.nr * self.nc)
        ]
        self.loc_circle = [(0, 0, 0, 0) for _ in range(self.nr * self.nc)]
        self._calculate_board_locations()

        frm = tk.Frame(pady=20, padx=20)
        frm.configure(background="#1f1f1f")

        canvas_width = self.coord_cells[-1][1][0] - self.coord_cells[0][-1][0]
        canvas_height = self.coord_cells[-1][3][1] - self.coord_cells[0][0][1]

        self.canvas = tk.Canvas(frm, width=canvas_width, height=canvas_height)
        self.canvas.configure(background="#1a1a1a")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        frm.grid_rowconfigure(0, weight=1)
        frm.grid_columnconfigure(0, weight=1)

        return frm

    def _init_log_frame(self) -> tk.Frame:
        """
        Initialize the log frame. This frame is used
        to display the log of the strategy generator.
        Any kind of error, or a message that the user
        needs to see, will be displayed in this frame.
        """
        frm = tk.Frame(padx=10, pady=10)

        # Add a label to the frame
        lbl_log = tk.Label(frm, text="Log:", font="Helvetica 14 bold")
        lbl_log.grid(row=0, column=0, sticky="nsew")

        # Log field. black background, white text.
        self.txt_log = tk.Text(
            frm,
            font="Helvetica 14",
            width=50,
            height=10,
            wrap=tk.WORD,
            bg="#1a1a1a",
            fg="#ffffff",
        )
        self.txt_log.grid(row=0, column=1, sticky="nsew")

        # make it scrollable
        self.scroll_log = tk.Scrollbar(frm, command=self.txt_log.yview)
        self.scroll_log.grid(row=0, column=2, sticky="nsew")
        self.txt_log.configure(yscrollcommand=self.scroll_log.set)

        Grid.columnconfigure(frm, 0, weight=1)
        Grid.columnconfigure(frm, 1, weight=5)
        Grid.rowconfigure(frm, 0, weight=1)

        return frm

    def _init_menu(self) -> tk.Menu:
        """
        Create the menu bar.
        """
        menu = tk.Menu(self.root)

        # create a pulldown menu, and add it to the menu bar
        gamemenu = tk.Menu(menu, tearoff=0)
        gamemenu.add_command(label="New game", command=self._init_new_game)
        gamemenu.add_command(label="Load game", command=self._init_load_game)
        gamemenu.add_command(label="Search in History",
                             command=self._init_search_history)
        gamemenu.add_command(label="Exit", command=self.root.quit)
        menu.add_cascade(label="Game", menu=gamemenu)

        # create more pulldown menus
        helpmenu = tk.Menu(menu, tearoff=0)
        helpmenu.add_command(label="About", command=self.about)
        menu.add_cascade(label="Help", menu=helpmenu)

        return menu

    def _init_new_game(self) -> None:
        """
        New popup window to get the new initial board, row and column size.
        """
        # Create a new popup window.
        self.new_init_win = tk.Toplevel(self.root)
        self.new_init_win.title("New Game")
        self.new_init_win.resizable(False, False)

        # Create the widgets.
        lbl_board_txt = tk.Label(self.new_init_win,
                                 text="Board in text:",
                                 anchor="e")
        lbl_row = tk.Label(self.new_init_win, text="Row size:", anchor="e")
        lbl_col = tk.Label(self.new_init_win, text="Column size:", anchor="e")
        # Ckeckbox for player 0 or 1.
        self.chk_player = tk.IntVar()
        self.chk_player.set(0)
        chk_player = tk.Checkbutton(
            self.new_init_win,
            text="First player",
            variable=self.chk_player,
            onvalue=0,
            offvalue=1,
        )
        # checkbox for if isomorphic
        self.chk_isomorphic = tk.IntVar()
        self.chk_isomorphic.set(0)
        chk_isomorphic = tk.Checkbutton(
            self.new_init_win,
            text="Isomorphic",
            variable=self.chk_isomorphic,
            onvalue=1,
            offvalue=0,
        )
        self.ent_board_txt = tk.Entry(self.new_init_win, width=25)
        self.ent_row = tk.Entry(self.new_init_win, width=5)
        self.ent_col = tk.Entry(self.new_init_win, width=5)
        self.ent_player = tk.Entry(self.new_init_win, width=5)
        btn_ok = tk.Button(self.new_init_win,
                           text="OK",
                           command=self.new_init_start)

        # Place the widgets.
        lbl_board_txt.grid(row=0, column=0, padx=5, pady=5)
        lbl_row.grid(row=1, column=0, padx=5, pady=5)
        lbl_col.grid(row=1, column=2, padx=5, pady=5)
        chk_player.grid(row=2, column=0, padx=5, pady=5, columnspan=2)
        chk_isomorphic.grid(row=2, column=2, padx=5, pady=5, columnspan=2)
        self.ent_board_txt.grid(row=0, column=1, padx=5, pady=5, columnspan=3)
        self.ent_row.grid(row=1, column=1, padx=5, pady=5)
        self.ent_col.grid(row=1, column=3, padx=5, pady=5)
        btn_ok.grid(row=3,
                    column=0,
                    padx=10,
                    pady=10,
                    sticky="ewsn",
                    columnspan=4)

    def _init_load_game(self) -> None:
        """Choose a history file to load the game from."""
        path = filedialog.askopenfilename(
            initialdir=os.path.join(os.getcwd(), "data"),
            title="Select a history file",
            filetypes=(("History files", "*.pkl"), ("All files", "*.*")),
        )
        if not path:
            # Failed, update the log.
            self.txt_log.insert(
                tk.END,
                "Failed to load the game.\n",
                ("error", "error"),
            )
            return
        # Load the history file.
        history = load_file(path)
        self.load_game(history)
        # Update the and the board.
        self.txt_log.insert(
            tk.END,
            "Loaded the game from {}.\n".format(path),
            ("info", "info"),
        )
        self.txt_log.see(tk.END)
        self.draw_board(self.strat_gen.board)
        self.ent_input.focus()
        # delete the entry and replace with the latest entry from history.
        self.ent_input.delete(0, tk.END)
        self.ent_input.insert(0, self.strat_gen.history_buffer.given_inputs[-1])

    def _init_end_game(self) -> None:
        """Pop up window to choose a location to save the file.
        Saves the file to location.
        """
        self.save_win = tk.Toplevel(self.root)
        self.save_win.title("End of game")
        self.save_win.resizable(False, False)

        # center the text
        label_file_explorer = tk.Label(self.save_win,
                                       text="Do you want to save the strategy?",
                                       anchor="center")
        button_save = tk.Button(self.save_win,
                                text="Save",
                                command=self.save_files)
        button_default_save = tk.Button(self.save_win,
                                        text="Save to default",
                                        command=self.save_file_default)
        button_cancel = tk.Button(self.save_win,
                                  text="Cancel",
                                  command=self.save_win.destroy)

        label_file_explorer.grid(row=0,
                                 column=0,
                                 padx=25,
                                 pady=25,
                                 columnspan=3,
                                 sticky="ewsn")
        button_save.grid(row=1, column=0, padx=25, pady=25, sticky="ewsn")
        button_default_save.grid(row=1,
                                 column=1,
                                 padx=25,
                                 pady=25,
                                 sticky="ewsn")
        button_cancel.grid(row=1, column=2, padx=25, pady=25, sticky="ewsn")

    def _init_search_history(self) -> None:
        """Pop up window to search information states in the history buffer
        Shows a list of all the states in the history buffer, and allows the user
        to search for a specific state, or pick from the list."""
        self.search_win = tk.Toplevel(self.root)
        self.search_win.title("Search history")
        self.search_win.resizable(False, False)

        # Create the widgets.
        lbl_search = tk.Label(self.search_win, text="Search:", anchor="e")
        self.ent_search = tk.Entry(self.search_win, width=25)
        self.list_search_result = tk.Listbox(self.search_win, width=25)
        self.fill_search_list('')
        btn_search = tk.Button(self.search_win,
                               text="Search",
                               command=self.search_history)
        self.ent_search.bind("<KeyRelease>",
                             self.search_history)  # bind to key release

        btn_select = tk.Button(self.search_win,
                               text="Select",
                               command=self.select_history)
        btn_cancel = tk.Button(self.search_win,
                               text="Cancel",
                               command=self.search_win.destroy)
        # add a scrollbar to the listbox
        scrollbar = tk.Scrollbar(self.search_win)
        scrollbar.config(command=self.list_search_result.yview)
        self.list_search_result.config(yscrollcommand=scrollbar.set)

        # Place the widgets.
        lbl_search.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.ent_search.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        btn_search.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        self.list_search_result.grid(row=1,
                                     column=0,
                                     padx=5,
                                     pady=5,
                                     sticky="ew",
                                     columnspan=3)
        btn_select.grid(row=2,
                        column=0,
                        padx=5,
                        pady=5,
                        sticky="ew",
                        columnspan=2)
        btn_cancel.grid(row=2, column=2, padx=5, pady=5, sticky="ew")

    def search_history(self, _=None):
        """Update the listbox with the search results."""
        self.fill_search_list(self.ent_search.get())

    def fill_search_list(self, search_phrase):
        """Fill the listbox with the history buffer."""
        self.list_search_result.delete(0, tk.END)
        for board in self.strat_gen.history_buffer.board:
            if search_phrase in board or search_phrase == '':
                self.list_search_result.insert(tk.END, board)

    def select_history(self):
        """Selects the selected item in the listbox, gets it's id and reverts the game
        to that state."""
        selected_item_str = self.list_search_result.get(
            self.list_search_result.curselection())
        if selected_item_str:
            self.strat_gen.history_buffer.revert_to_state(
                state=selected_item_str)
            self.draw_board(self.strat_gen.board)
            self.ent_input.delete(0, tk.END)
            try:
                self.ent_input.insert(
                    0, self.strat_gen.history_buffer.given_inputs[-1])
            except IndexError:
                pass
            self.search_win.destroy()

    def _calculate_board_locations(self) -> None:
        """Calculates every coordinates needed, to use later on."""
        # Calculate cell locations
        cell_id = 0
        len_sq = self.len_ce * math.sqrt(3) / 2
        for row in range(self.nr):
            for col in range(self.nc):
                # Draw the cell.
                x = len_sq + row * len_sq + 2 * col * len_sq
                y = 1.5 * row * self.len_ce
                loc = (
                    (x, y),  # top-middle
                    (x + len_sq, y + self.len_ce * 0.5),  # top-right
                    (x + len_sq, y + self.len_ce * 1.5),  # bottom-right
                    (x, y + 2 * self.len_ce),  # bottom-middle
                    (x - len_sq, y + self.len_ce * 1.5),  # bottom-left
                    (x - len_sq, y + self.len_ce * 0.5),  # top-left
                )
                # Save the center of the cell.
                self.loc_circle[cell_id] = (
                    x - self.r,
                    y + self.len_ce - self.r,
                    x + self.r,
                    y + self.len_ce + self.r,
                )
                self.loc_cen[cell_id] = (x, y + self.len_ce)
                # Save the cell coordinates.
                self.coord_cells[cell_id] = loc
                cell_id += 1

    def draw_board(self, board_str: str) -> None:
        self.canvas.delete("all")
        for cell_id in range(self.nr * self.nc):
            self._draw_cell(board_str[cell_id], cell_id)

    def _draw_cell(self, cell_str: str, cell_id: int) -> None:
        """Draws a cell on the canvas."""
        # Draw the cell.
        self.canvas.create_polygon(
            self.coord_cells[cell_id],
            fill=colors["."],
            outline=colors["black"],
            width=4,
        )
        # Draw the cell's content.
        if cell_str in cellState.black_pieces:
            self.canvas.create_oval(
                self.loc_circle[cell_id],
                fill=colors["x"],
                outline=colors["black"],
                width=4,
            )
        elif cell_str in cellState.white_pieces:
            self.canvas.create_oval(
                self.loc_circle[cell_id],
                fill=colors["o"],
                outline=colors["black"],
                width=4,
            )
        # Draw the cell id.
        # convert cell_id to alphanumeric id
        text_id = chr(ord("a") + cell_id % self.nc) + str(cell_id // self.nc +
                                                          1)
        self.canvas.create_text(self.loc_cen[cell_id],
                                text=str(text_id),
                                fill=colors["white"])

    def enter(self) -> None:
        the_in = self.ent_input.get()
        # run the strategy generator
        success, log, new_board, end_game = self.strat_gen.iterate_board(the_in)

        log = "Move succeeded.\n" + log if success else "Move failed.\n" + log
        self.txt_log.insert(tk.END, log + "\n")
        self.txt_log.see(tk.END)
        self.draw_board(new_board)
        self.ent_input.delete(0, "end")
        if end_game:
            self._init_end_game()

    def random_input(self) -> None:
        success, log, new_board, end_game = self.strat_gen.iterate_board(
            "random_roll")

        log = "Random roll succeded \n" + log if success else "Random roll failed.\n" + log
        self.txt_log.insert(tk.END, log + "\n")
        self.txt_log.see(tk.END)
        self.draw_board(new_board)
        self.ent_input.delete(0, "end")
        if end_game:
            self._init_end_game()

    def _save_to(self, path) -> str:
        data = {
            "num_cols": self.nc,
            "num_rows": self.nr,
            "player": self.player,
            "isomorphic": self.include_isomorphic,
            "initial_board": self.initial_board,
            "strategy": self.strat_gen.info_states,
        }
        # save the file
        save_file(data, path + "/game_info.pkl")
        save_file(self.strat_gen.history_buffer, path + "/history.pkl")
        return path

    def save_file_default(self) -> None:
        """Saves the file to the default location."""
        # default location is data/nrxnc_new/game_info.pkl
        # find data
        data_dir = os.path.join(
            os.path.dirname(__file__),
            f"../data/strategy_data/{self.nr}x{self.nc}_{self.player}_def",
        )
        # create the directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        # save the file
        path = self._save_to(data_dir)
        self.txt_log.insert(tk.END,
                            "File saved to " + path + "/game_info.pkl\n")
        self.txt_log.insert(
            tk.END, "History buffer saved to " + path + "/history.pkl\n")
        self.txt_log.see(tk.END)
        self.save_win.destroy()

    def save_files(self):
        # get the file name
        # start from the current directory
        cur_dir = os.getcwd()
        path = filedialog.asksaveasfilename(
            initialdir=cur_dir + "darkhex/data/",
            title="Select a Folder",
            filetypes=(("all files", "*.*"), ("python files", "*.pkl")),
        )
        path = self._save_to(path)
        self.txt_log.insert(tk.END,
                            "File saved to " + path + "/game_info.pkl\n")
        self.txt_log.insert(tk.END,
                            "History file saved to " + path + "/history.pkl\n")
        self.txt_log.see(tk.END)
        self.save_win.destroy()

    def rewind(self) -> None:
        log = self.strat_gen.history_buffer.rewind()
        self.txt_log.insert(tk.END, log)
        self.txt_log.see(tk.END)
        self.draw_board(self.strat_gen.board)
        self.ent_input.delete(0, "end")
        if len(self.strat_gen.history_buffer.given_inputs) > 0:
            old_input = self.strat_gen.history_buffer.given_inputs[-1]
            self.ent_input.insert(0, old_input)

    def restart(self) -> None:
        log = self.strat_gen.history_buffer.restart()
        self.txt_log.insert(tk.END, log)
        self.txt_log.see(tk.END)
        self.draw_board(self.strat_gen.board)

    def about(self) -> None:
        messagebox.showinfo("About", "This is a strategy generator.")

    def new_init_start(self) -> None:
        """
        Start the new initial board.
        """
        # Get the input.
        board_txt = self.ent_board_txt.get()
        row = int(self.ent_row.get())
        col = int(self.ent_col.get())
        isomorphic = self.chk_isomorphic.get()
        player = self.chk_player.get()
        # Check if the input is valid.
        if not board_txt:
            messagebox.showwarning("Warning", "Please input the board.")
            return
        if not row or not col:
            messagebox.showwarning("Warning",
                                   "Please input the row and column size.")
            return
        # Close the popup window.
        self.new_init_win.destroy()
        self._setup_game(board_txt, row, col, player, isomorphic)
        # Clear the log.
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.insert(tk.END, f"New game started.\n{self.nr}x{self.nc}\n")
        # Draw the board.
        self.draw_board(self.strat_gen.board)

    def load_game(self, history: gameBuffer):
        """Given history, sets up the StrategyGenerator and gameBuffers."""
        self._setup_game(history.game_info["initial_board"],
                         history.game_info["num_rows"],
                         history.game_info["num_cols"],
                         history.game_info["player"],
                         history.game_info["isomorphic"])
        self.strat_gen.load_game(history)


class StrategyGenerator:

    def __init__(
        self,
        initial_board: str,
        num_rows: int,
        num_cols: int,
        player: int,
        include_isomorphic: bool = True,
    ):
        self.num_cols = num_cols
        self.num_rows = num_rows
        self.p = player
        self.o = 1 - self.p
        self.include_isomorphic = include_isomorphic

        # Perform Checks to see if initial values are valid
        if not is_valid_board(initial_board, num_rows, num_cols):
            raise ValueError("Invalid initial board")

        self.board = initial_board
        self.info_states = {}
        self.moves_and_boards = {}
        self.move_stack = []

        self.random_roll = False  # if true, take actions until the terminal state.
        self.target_stack_board = None

        # set history buffer
        self.history_buffer = gameBuffer(initial_board, num_rows, num_cols,
                                         player, include_isomorphic, self)

    def iterate_board(self, given_input: str) -> None:
        """Iterate the board with the given action.

        Update the information states and the strategy.
        """
        # Check if the given input is valid.
        success, actions, probs, log = self.is_valid_moves(
            self.board, given_input)
        if not success:
            return False, log, self.board, False
        # log the move type
        log = f"{log}\n{actions} / {given_input}\n"
        self.info_states[self.board] = self._action_probs(actions, probs)

        if self.include_isomorphic:
            iso_state, iso_moves_probs = isomorphic_single(
                self.board, actions, probs)
            if iso_state not in self.info_states:
                self.info_states[iso_state] = iso_moves_probs
            else:
                ls = []
                d = {}
                for move, prob in iso_moves_probs:
                    if move not in d:
                        ls.append((move, prob / 2))
                        d[move] = len(ls) - 1
                    else:
                        ls[d[move]] = (move, ls[d[move]][1] + prob / 2)
                for move, prob in self.info_states[iso_state]:
                    if move not in d:
                        ls.append((move, prob / 2))
                        d[move] = len(ls) - 1
                    else:
                        ls[d[move]] = (move, ls[d[move]][1] + prob / 2)
                self.info_states[iso_state] = ls

        collusion_possible = self._is_collusion_possible()
        addition = 0
        for action in actions:
            new_board = self.moves_and_boards[f"{action}{self.p}"]
            if self._is_terminal(new_board):
                log += f"Terminal state reached with action {action}\n"
            elif new_board not in self.info_states:
                self.move_stack.append(new_board)
                addition += 1
            if collusion_possible:
                new_board = self.moves_and_boards[f"{action}{self.o}"]
                if self._is_terminal(new_board):
                    log += f"Terminal state reached with action {action}\n"
                elif new_board not in self.info_states:
                    self.move_stack.append(new_board)
                    addition += 1
        if len(self.move_stack) == 0:
            self.history_buffer.add_history_buffer(self, given_input)
            return (
                True,
                log + f"Game has ended. No more moves to make.\n",
                self.board,
                True,
            )
        self.board = self.move_stack.pop()
        self.history_buffer.add_history_buffer(self, given_input)
        print(self.move_stack, addition, self.board)
        if self.random_roll:
            self.random_roll = False
            self.target_stack_board = deepcopy(self.move_stack[-addition])
        if self.target_stack_board:
            if self.target_stack_board == self.board:
                self.target_stack_board = None
            else:
                self.iterate_board("random_roll")
        return True, log + "Move performed succeded.\n", self.board, False

    def is_valid_moves(
        self, board: str, given_input: str
    ) -> typing.Tuple[bool, typing.List[int], typing.List[float]]:
        success, moves, probs = self._get_moves(board, given_input)
        if not success:
            return False, None, None, f"Invalid move: {moves}"
        # Check if the moves are valid. Save the new board states for each move.
        self.moves_and_boards = {}
        for move in moves:
            o_color = "o" if self.p == 0 else "x"
            p_color = "x" if self.p == 0 else "o"
            new_board = updated_board(board, move, o_color, self.num_rows,
                                      self.num_cols)
            new_board_2 = updated_board(board, move, p_color, self.num_rows,
                                        self.num_cols)
            if not new_board:
                return False, None, None, f"Invalid move: {move}"
            self.moves_and_boards[f"{move}{self.o}"] = new_board
            self.moves_and_boards[f"{move}{self.p}"] = new_board_2
        # check if sum of probs is 1
        if abs(sum(probs) - 1) > 0.0000001:  # python float comparison
            return False, None, None, f"Values don't add up to one: {probs}->{sum(probs)}"
        return True, moves, probs, "Values processed successfully."

    def _get_moves(self, board: str, given_input: str):
        if len(given_input) < 1:
            return False, "No action given.", None
        action_probs = given_input.strip().split(" ")
        if action_probs[0] == "random_roll":
            if self.target_stack_board is None:
                self.random_roll = True
            move = board.find('.')
            return True, [move], [1]
        if len(action_probs) == 1:
            a = num_action(action_probs[0], self.num_cols)
            if isinstance(a, int):
                moves = [a]
                probs = [1]
            else:
                return False, action_probs, None
        elif action_probs[0] == "=":
            moves = [num_action(x, self.num_cols) for x in action_probs[1:]]
            if False in moves:
                return False, action_probs, None
            probs = [1 / len(moves)] * len(moves)
        else:
            moves = []
            probs = []
            for i in range(0, len(action_probs), 2):
                a = num_action(action_probs[i], self.num_cols)
                if a:
                    moves.append(a)
                    probs.append(float(action_probs[i + 1]))
                else:
                    return False, action_probs, None
        moves = list(map(int, moves))
        probs = list(map(float, probs))
        return True, moves, probs

    def _action_probs(self,
                      actions: typing.List[int],
                      probs: typing.List[float] = None
                     ) -> typing.List[typing.Tuple[int, float]]:
        """Returns the action probs for the current board."""
        if probs is None:
            probs = [1 / len(actions)] * len(actions)
        else:
            assert len(actions) == len(probs)
        return list(zip(actions, probs))

    def _is_collusion_possible(self) -> bool:
        """
        Check if a collusion is possible.
        """
        # Get the number of cellState on the board.
        count = Counter(self.board)
        if self.p == 1:
            player_pieces = sum(
                [s for x, s in count.items() if x in cellState.white_pieces])
            opponent_pieces = sum(
                [s for x, s in count.items() if x in cellState.black_pieces])
            return opponent_pieces <= player_pieces
        player_pieces = sum(
            [s for x, s in count.items() if x in cellState.black_pieces])
        opponent_pieces = sum(
            [s for x, s in count.items() if x in cellState.white_pieces])
        return opponent_pieces < player_pieces

    def _is_terminal(self, board_state):
        """
        Check if the game is over.

        - board_state: The current board state.
        """
        if (board_state.count(cellState.kBlackWin) +
                board_state.count(cellState.kWhiteWin) > 0):
            return True
        ct = Counter(board_state)
        empty_cells = ct[cellState.kEmpty]
        if self.p == 0:
            opponent_pieces = sum(
                [s for x, s in ct.items() if x in cellState.white_pieces])
            player_pieces = sum(
                [s for x, s in ct.items() if x in cellState.black_pieces])
            if opponent_pieces + empty_cells == player_pieces:
                return True
        else:
            opponent_pieces = sum(
                [s for x, s in ct.items() if x in cellState.black_pieces])
            player_pieces = sum(
                [s for x, s in ct.items() if x in cellState.white_pieces])
            if opponent_pieces + empty_cells == player_pieces + 1:
                return True
        return False

    def load_game(self, history: gameBuffer):
        """Load a game from a history buffer."""
        self.num_cols = history.game_info["num_cols"]
        self.num_rows = history.game_info["num_rows"]
        self.p = history.game_info["player"]
        self.o = 1 - self.p
        self.history_buffer = history
        self.history_buffer.stratgen_class = self
        self.board = history.board[-1]
        self.move_stack = history.move_stack[-1]
        self.moves_and_boards = history.moves_and_boards[-1]
        self.info_states = history.info_states[-1]


def is_valid_board(board: str, num_rows: int, num_cols: int) -> bool:
    """Check if the given board is valid."""
    # TODO: Complete this function.
    if len(board) != num_rows * num_cols:
        return False
    return True
