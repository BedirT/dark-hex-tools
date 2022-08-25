import tkinter as tk
import customtkinter as ctk
import math
from darkhex import cellState
import typing
import darkhex.utils.util as util
from darkhex.gui.strategy_generator import StrategyGenerator
from darkhex import logger as log
import datetime
import os
import copy


class PolicyGenGUI(ctk.CTk):
    """ Using customtkinter grid system to create a GUI for the policy generator. """

    # --- VISUAL COMPONENTS ---

    COLORS = {
        "black": "#000000",
        "white": "#ffffff",
        ".": "#357EC7",
        "x": "#2b2222",
        "o": "#c7b6a3",
        "red": "#C34A2C",
        "red_hover": "#7E3517",
    }

    WIDTH = 1200
    HEIGHT = 600

    LEFT_FRAME_WIDTH = 180
    LOG_WIDTH = 180
    BOARD_WIDTH = 500
    CELL_PADDING = 20

    FONT_BUTTON = ("Roboto Bold", -12)
    FONT_LABEL = ("Roboto Medium", -12)
    FONT_LOGO = ("Ubuntu", -20)
    FONT_TEXTBOX = "Helvetica 14"

    def __init__(self):
        super().__init__()
        self.setup_game(4,
                        3,
                        False,
                        1,
                        perfect_recall=True,
                        include_isomorphic=False)

    def setup_main_frame(self):
        self.title("Policy Generator")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.resizable(True, True)
        self.minsize(self.WIDTH, self.HEIGHT)

        # ----- Layout arrangement: Creating the main frames -----
        # We have 2 frames
        # Setup the frame rows and column
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Creating the frames
        self.frame_left = ctk.CTkFrame(master=self,
                                       width=self.LEFT_FRAME_WIDTH,
                                       corner_radius=0)
        self.frame_right = ctk.CTkFrame(master=self, corner_radius=10)

        # Placing the frames on the grid
        self.frame_left.grid(row=0, column=0, sticky="nsew")
        self.frame_right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # ----- Layout arrangement: Filling the left frame -----
        # Left frame has 11x1 grid
        # All grids have weight 1 so we are not mentioning, except we fill the
        # rows to create some gaps.
        self.frame_left.grid_rowconfigure(0, minsize=10)
        self.frame_left.grid_rowconfigure(1, minsize=40)  # row 1 is for logo
        self.frame_left.grid_rowconfigure(5, weight=1)
        self.frame_left.grid_rowconfigure(11, minsize=10)  # for the bottom gap

        self.setup_left_frame()

        # ----- Layout arrangement: Filling the right frame -----
        # Right frame has 2x2 grid
        self.frame_right.grid_columnconfigure(0,
                                              weight=1,
                                              minsize=self.LOG_WIDTH)
        self.frame_right.grid_columnconfigure(1,
                                              weight=10,
                                              minsize=self.BOARD_WIDTH)
        self.frame_right.grid_rowconfigure(0, weight=1)
        self.frame_right.grid_rowconfigure(1, weight=3)

        self.setup_history_frame()
        self.setup_log_frame()
        self.setup_board_frame()
        self.setup_actions_frame()

        self.setup_right_frame()

        self.draw_board(self.board_state)
        self.setup_bindings()

        # set default values
        self.menu_appearance.set("Dark")

    def reload_board(self, event):
        self.frame_board.update_idletasks()
        self.draw_board(self.board_state)

    def setup_game(self,
                   num_rows: int,
                   num_cols: int,
                   pone: bool,
                   player: int,
                   initial_board: str = "",
                   include_isomorphic: bool = True,
                   perfect_recall: bool = False):
        """ Sets up the game. """
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.pone = pone
        self.player = player
        self.include_isomorphic = include_isomorphic
        self.perfect_recall = perfect_recall
        if self.perfect_recall and self.include_isomorphic:
            raise ValueError(
                "Perfect recall is not compatible with isomorphic games.")
        # using open_spiels game representations
        self.board_state = initial_board if initial_board else util.flat_board_to_layered('.' * (
            self.num_rows * self.num_cols), self.num_cols)
        if self.perfect_recall:
            self.action_sequence = []
            self.history = []
            if (self.history or self.action_sequence
               ) and self.board_state != '.' * (self.num_rows * self.num_cols):
                raise ValueError(
                    "Given a non empty board state and empty history or action sequence. The actions"
                    + " sequence and history must be matching the board state.")
            self.initial_state = util.get_perfect_recall_state(
                self.player, self.board_state, self.action_sequence)
        else:
            self.initial_state = util.get_imperfect_recall_state(
                self.player, self.board_state)
        self.strat_gen = StrategyGenerator(self.initial_state, self.num_rows,
                                           self.num_cols, self.player,
                                           self.include_isomorphic,
                                           self.perfect_recall)

        self.information_state = copy.deepcopy(self.initial_state)
        self.setup_main_frame()

    def setup_left_frame(self):
        # create the items
        self.label_logo = ctk.CTkLabel(master=self.frame_left,
                                       text="PolGen",
                                       text_font=self.FONT_LOGO)
        self.button_new_policy = ctk.CTkButton(master=self.frame_left,
                                               text="New Policy",
                                               text_font=self.FONT_BUTTON,
                                               command=self.setup_new_policy)
        self.button_load_policy = ctk.CTkButton(master=self.frame_left,
                                                text="Load Policy",
                                                text_font=self.FONT_BUTTON,
                                                command=self.on_load_policy,
                                                state=tk.DISABLED)
        self.label_ap_mode = ctk.CTkLabel(
            master=self.frame_left,
            text="Appearance Mode:",
            justify=tk.LEFT,
            anchor=tk.S,
        )
        self.menu_appearance = ctk.CTkOptionMenu(
            master=self.frame_left,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode)
        self.label_credit = ctk.CTkLabel(master=self.frame_left,
                                         text="Created by Bedir Tapkan",
                                         text_font=self.FONT_LABEL,
                                         justify=tk.CENTER,
                                         text_color="grey")

        # place the items
        self.label_logo.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.button_new_policy.grid(row=2,
                                    column=0,
                                    sticky="nsew",
                                    padx=20,
                                    pady=10)
        self.button_load_policy.grid(row=3,
                                     column=0,
                                     sticky="nsew",
                                     padx=20,
                                     pady=10)
        self.label_ap_mode.grid(row=8,
                                column=0,
                                sticky="nse",
                                padx=20,
                                pady=(10, 3))
        self.menu_appearance.grid(row=9,
                                  column=0,
                                  sticky="nsew",
                                  padx=20,
                                  pady=(0, 5))
        self.label_credit.grid(row=10, column=0, sticky="nsew", padx=20, pady=5)

    def setup_history_frame(self):
        self.frame_info_state_history = ctk.CTkFrame(master=self.frame_right)
        self.frame_info_state_history.rowconfigure(1, weight=1)
        self.frame_info_state_history.columnconfigure(0, weight=1)
        # creating the items for subframes
        self.label_info_state_history = ctk.CTkLabel(
            master=self.frame_info_state_history,
            text="Information State History:",
            text_font=self.FONT_LABEL,
            justify=tk.LEFT,
            anchor=tk.NW)
        self.text_info_state_history = tk.Text(
            master=self.frame_info_state_history,
            font=self.FONT_TEXTBOX,
            wrap=tk.WORD,
            state=tk.DISABLED,
            background="#52595D",
            foreground="#CECECE",
            highlightthickness=0,
            relief=tk.FLAT,
            padx=10,
            pady=10)
        # add scrollbar to text widget
        self.scrollbar_info_state_history = ctk.CTkScrollbar(
            master=self.frame_info_state_history,
            command=self.text_info_state_history.yview)
        self.text_info_state_history.configure(
            yscrollcommand=self.scrollbar_info_state_history.set)

        # placing the items on subframes
        self.label_info_state_history.grid(row=0,
                                           column=0,
                                           sticky="nwes",
                                           padx=10,
                                           pady=(10, 0))
        self.text_info_state_history.grid(row=1,
                                          column=0,
                                          sticky="news",
                                          padx=10,
                                          pady=(0, 10))

    def setup_log_frame(self):
        self.frame_logs = ctk.CTkFrame(master=self.frame_right)

        self.frame_logs.rowconfigure(1, weight=1)
        self.frame_logs.columnconfigure(0, weight=1)
        self.label_logs = ctk.CTkLabel(master=self.frame_logs,
                                       text="Logs:",
                                       text_font=self.FONT_LABEL,
                                       justify=tk.LEFT,
                                       anchor=tk.NW)
        self.text_logs = tk.Text(master=self.frame_logs,
                                 font=self.FONT_TEXTBOX,
                                 wrap=tk.WORD,
                                 state=tk.DISABLED,
                                 background="#52595D",
                                 foreground="#CECECE",
                                 highlightthickness=0,
                                 relief=tk.FLAT,
                                 padx=10,
                                 pady=10)
        # add scrollbar to text widget
        self.scrollbar_logs = ctk.CTkScrollbar(master=self.frame_logs,
                                               command=self.text_logs.yview)
        self.text_logs.configure(yscrollcommand=self.scrollbar_logs.set)

        # placing the items on subframes
        self.label_logs.grid(row=0,
                             column=0,
                             sticky="nwes",
                             padx=10,
                             pady=(10, 0))
        self.text_logs.grid(row=1,
                            column=0,
                            sticky="news",
                            padx=10,
                            pady=(0, 10))

    def setup_board_frame(self):
        """ Sets up the board frame """
        self.frame_board = self._init_board_frame()

        self.frame_board.update()
        canvas_width = self.frame_board.winfo_width()
        canvas_height = self.frame_board.winfo_height()

        # Frame board is 1x1 grid
        self.frame_board.rowconfigure(0, weight=1)
        self.frame_board.columnconfigure(0, weight=1)

    def setup_actions_frame(self):
        # Frame actions is 3x4 grid
        self.frame_actions = ctk.CTkFrame(master=self.frame_right)
        self.frame_actions.rowconfigure((0, 1, 2), weight=1)
        self.frame_actions.columnconfigure((0, 1, 2), weight=1)

        # creating the widgets for the actions frame
        self.label_current_info_state_title = ctk.CTkLabel(
            master=self.frame_actions,
            text="Current Info State:",
            justify=tk.RIGHT,
            anchor=tk.E,
        )
        self.label_current_info_state = ctk.CTkLabel(
            master=self.frame_actions,
            text=self.strat_gen.current_info_state,
            justify=tk.LEFT,
            anchor=tk.W)
        self.entry_text_variable = tk.StringVar()
        self.entry_action_probs = ctk.CTkEntry(
            master=self.frame_actions,
            textvariable=self.entry_text_variable,
        )
        self.button_execute_action = ctk.CTkButton(master=self.frame_actions,
                                                   text="Execute Action",
                                                   command=self.execute_action)
        self.button_random = ctk.CTkButton(
            master=self.frame_actions,
            text="Random",
            command=self.random_action)  # todo: change with an icon instead
        self.button_rewind = ctk.CTkButton(
            master=self.frame_actions,
            text="Rewind",
            command=self.rewind_action)  # todo: change with an icon instead
        self.button_restart = ctk.CTkButton(
            master=self.frame_actions,
            text="Restart",
            fg_color=self.COLORS["red"],
            hover_color=self.COLORS["red_hover"],
            command=self.restart_game)  # todo: change with an icon instead

        # placing the items on the actions frame
        self.label_current_info_state_title.grid(row=0,
                                                 column=0,
                                                 sticky="nes",
                                                 padx=10,
                                                 pady=(10, 0))
        self.label_current_info_state.grid(row=0,
                                           column=1,
                                           columnspan=2,
                                           sticky="nws",
                                           padx=10,
                                           pady=(10, 0))
        self.entry_action_probs.grid(row=1,
                                     column=0,
                                     columnspan=2,
                                     sticky="news",
                                     padx=10,
                                     pady=(0, 10))
        self.button_execute_action.grid(row=1,
                                        column=2,
                                        sticky="news",
                                        padx=10,
                                        pady=(0, 10))
        self.button_random.grid(row=2,
                                column=0,
                                sticky="news",
                                padx=10,
                                pady=(0, 10))
        self.button_rewind.grid(row=2,
                                column=1,
                                sticky="news",
                                padx=10,
                                pady=(0, 10))
        self.button_restart.grid(row=2,
                                 column=2,
                                 sticky="news",
                                 padx=10,
                                 pady=(0, 10))

    def setup_right_frame(self):
        """ Placing the items on the right frame """
        self.frame_info_state_history.grid(row=0,
                                           column=0,
                                           sticky="nsew",
                                           padx=(10, 10),
                                           pady=(10, 10))
        self.frame_logs.grid(row=1,
                             column=0,
                             sticky="nsew",
                             padx=(10, 10),
                             pady=(0, 10))

        self.frame_board.grid(row=0,
                              column=1,
                              sticky="nsew",
                              padx=(0, 10),
                              pady=(10, 10),
                              ipadx=10,
                              ipady=10)
        self.frame_actions.grid(row=1,
                                column=1,
                                sticky="nsew",
                                padx=(0, 10),
                                pady=(0, 10))

    def setup_end_game(self) -> None:
        """Pop up window to choose a location to save the file.
        Saves the file to location.
        """
        self.save_win = ctk.CTkToplevel(master=self)
        self.save_win.title("End of game")
        self.save_win.resizable(False, False)

        label_file_explorer = ctk.CTkLabel(
            master=self.save_win,
            text="The strategy is complete, do you want to save?",
            anchor=tk.CENTER)

        # create the buttons
        button_save = ctk.CTkButton(master=self.save_win,
                                    text="Save",
                                    command=self.save_file)
        button_cancel = ctk.CTkButton(master=self.save_win,
                                      text="Cancel",
                                      command=self.save_win.destroy)
        button_default_save = ctk.CTkButton(master=self.save_win,
                                            text="Save to default",
                                            command=self.save_file_default)

        # place the widgets
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

    def setup_new_policy(self):
        """
        New popup window to get the new initial board, row and column size.
        """
        self.new_policy_win = ctk.CTkToplevel(master=self)
        self.new_policy_win.title("New policy setup")
        self.new_policy_win.resizable(False, False)

        # create the widgets
        label_row_size = ctk.CTkLabel(master=self.new_policy_win,
                                      text="Number of Rows:",
                                      anchor=tk.E)
        label_column_size = ctk.CTkLabel(master=self.new_policy_win,
                                         text="Number of Columns:",
                                         anchor=tk.E)
        label_initial_board = ctk.CTkLabel(master=self.new_policy_win,
                                           text="Initial board:",
                                           anchor=tk.E)

        self.var_row_size = tk.IntVar()
        self.var_column_size = tk.IntVar()
        self.var_initial_board = tk.StringVar()
        self.var_perfect_recall = tk.BooleanVar()
        self.var_isomorphic = tk.BooleanVar()
        self.var_pone = tk.BooleanVar()
        self.var_player = tk.BooleanVar()

        self.var_row_size.set(self.num_rows)
        self.var_column_size.set(self.num_cols)
        self.var_initial_board.set(self.board_state)
        self.var_perfect_recall.set(self.perfect_recall)
        self.var_isomorphic.set(self.include_isomorphic)
        self.var_pone.set(self.pone)
        self.var_player.set(self.player)

        entry_row_size = ctk.CTkEntry(master=self.new_policy_win,
                                      width=5,
                                      textvariable=self.var_row_size)
        entry_column_size = ctk.CTkEntry(master=self.new_policy_win,
                                         width=5,
                                         textvariable=self.var_column_size)
        entry_initial_board = ctk.CTkEntry(master=self.new_policy_win,
                                           width=25,
                                           textvariable=self.var_initial_board)
        self.checkbox_perfect_recall = ctk.CTkSwitch(
            master=self.new_policy_win,
            text="Perfect recall",
            command=self.perfect_recall_toggle)
        self.checkbox_isomorphic = ctk.CTkSwitch(master=self.new_policy_win,
                                                 text="Isomorphic")
        self.checkbox_pone = ctk.CTkSwitch(master=self.new_policy_win,
                                           text="Pone")
        self.checkbox_player = ctk.CTkSwitch(master=self.new_policy_win,
                                             text="First Player",
                                             onvalue=0,
                                             offvalue=1)

        button_ok = ctk.CTkButton(master=self.new_policy_win,
                                  text="OK",
                                  command=self.new_policy)
        button_cancel = ctk.CTkButton(master=self.new_policy_win,
                                      text="Cancel",
                                      command=self.new_policy_win.destroy)
        # place the widgets
        label_row_size.grid(row=0, column=0, padx=5, pady=5, sticky="ewsn")
        label_column_size.grid(row=1, column=0, padx=5, pady=5, sticky="ewsn")
        label_initial_board.grid(row=2, column=0, padx=5, pady=5, sticky="ewsn")
        entry_row_size.grid(row=0, column=1, padx=5, pady=5, sticky="ewsn")
        entry_column_size.grid(row=1, column=1, padx=5, pady=5, sticky="ewsn")
        entry_initial_board.grid(row=2, column=1, padx=5, pady=5, sticky="ewsn")

        self.checkbox_perfect_recall.grid(row=0,
                                          column=2,
                                          padx=10,
                                          pady=10,
                                          sticky="ewsn")
        self.checkbox_isomorphic.grid(row=1,
                                      column=2,
                                      padx=10,
                                      pady=10,
                                      sticky="ewsn")
        self.checkbox_pone.grid(row=2,
                                column=2,
                                padx=10,
                                pady=10,
                                sticky="ewsn")
        self.checkbox_player.grid(row=3,
                                  column=2,
                                  padx=10,
                                  pady=10,
                                  sticky="ewsn")
        button_ok.grid(row=4, column=1, padx=10, pady=10, sticky="ewsn")
        button_cancel.grid(row=4, column=2, padx=10, pady=10, sticky="ewsn")

    def perfect_recall_toggle(self):
        if self.checkbox_perfect_recall.get():
            self.checkbox_isomorphic.deselect()
            self.checkbox_pone.deselect()
            self.checkbox_isomorphic.configure(state=tk.DISABLED)
            self.checkbox_pone.configure(state=tk.DISABLED)
        else:
            self.checkbox_isomorphic.configure(state=tk.NORMAL)
            self.checkbox_pone.configure(state=tk.NORMAL)

    def change_appearance_mode(self, new_appearance_mode):
        """ Changes the appearance mode. """
        ctk.set_appearance_mode(new_appearance_mode)

    # --- FUNCTIONALITY ---

    def setup_bindings(self):
        # ctrl + d to exit
        self.bind("<Control-d>", self.on_closing)
        # ctrl + n to create a new policy
        self.bind("<Control-n>", self.setup_new_policy)
        # ctrl + o to open a policy (load)
        self.bind("<Control-o>", self.on_load_policy)
        # alt + r for random action
        self.bind("<Alt-r>", lambda event: self.random_action())
        # ctrl + z for rewind
        self.bind("<Control-z>", self.rewind_action)
        # ctrl + r for reloading the board
        self.bind("<Control-r>", self.reload_board)
        # Enter to submit the textbox
        self.entry_action_probs.bind("<Return>",
                                     lambda event: self.execute_action())

    def new_policy(self):
        """
        Create a new policy.
        """
        self.setup_game(num_rows=int(self.var_row_size.get()),
                        num_cols=int(self.var_column_size.get()),
                        initial_board=self.var_initial_board.get(),
                        perfect_recall=self.checkbox_perfect_recall.get(),
                        include_isomorphic=self.checkbox_isomorphic.get(),
                        pone=self.checkbox_pone.get(),
                        player=self.checkbox_player.get())
        self.new_policy_win.destroy()

    def on_load_policy(self):
        """ Loads a policy. """
        pass

    def on_closing(self):
        """ Closes the window. """
        self.destroy()

    def execute_action(self) -> None:
        the_in = self.entry_text_variable.get()
        # run the strategy generator
        new_board, end_game = self.strat_gen.iterate_board(the_in)
        log.debug(msg="new board: {}".format(new_board))
        log.debug(msg="end game: {}".format(end_game))
        log.debug(f"info_state: {self.strat_gen.current_info_state}")

        self.draw_board(util.layered_board_to_flat(new_board))
        self.entry_text_variable.set("")
        if end_game:
            self.setup_end_game()

    def random_action(self):
        """ Randomly selects an action. """
        new_board, end_game = self.strat_gen.iterate_board("random_roll")
        self.draw_board(new_board)
        self.entry_text_variable.set("")
        if end_game:
            self.setup_end_game()

    def rewind_action(self):
        """ Rewinds the game. """
        self.strat_gen.history_buffer.rewind()
        self.draw_board(self.strat_gen.board)
        self.entry_text_variable.set("")
        if len(self.strat_gen.history_buffer.given_inputs) > 0:
            old_input = self.strat_gen.history_buffer.given_inputs[-1]
            self.entry_text_variable.set(old_input)

    def restart_game(self):
        """ Restarts the game. """
        self.strat_gen.history_buffer.restart()
        self.draw_board(self.strat_gen.board)

    def draw_board(self, board_str: str) -> None:
        self.canvas.delete("all")
        self.calculate_board_locations()
        for cell_id in range(self.num_rows * self.num_cols):
            self._draw_cell(board_str[cell_id], cell_id)
        self.label_current_info_state.set_text(
            self.strat_gen.current_info_state)

    def _draw_cell(self, cell_str: str, cell_id: int) -> None:
        """Draws a cell on the canvas."""
        # Draw the cell.
        self.canvas.create_polygon(
            self.coord_cells[cell_id],
            fill=self.COLORS["."],
            outline=self.frame_board.cget("bg"),
            width=4,
        )
        # Draw the cell's content.
        if cell_str in cellState.black_pieces:
            self.canvas.create_oval(
                self.loc_circle[cell_id],
                fill=self.COLORS["x"],
                outline=self.COLORS["black"],
                width=4,
            )
        elif cell_str in cellState.white_pieces:
            self.canvas.create_oval(
                self.loc_circle[cell_id],
                fill=self.COLORS["o"],
                outline=self.COLORS["black"],
                width=4,
            )
        # Draw the cell id.
        # convert cell_id to alphanumeric id
        text_id = chr(ord("a") + cell_id %
                      self.num_cols) + str(cell_id // self.num_cols + 1)
        self.canvas.create_text(self.loc_cen[cell_id],
                                text=str(text_id),
                                fill=self.COLORS["white"])

    def _init_board_frame(self) -> tk.Frame:
        frm = ctk.CTkFrame(
            master=self.frame_right,
            pady=10,
            padx=10,
            relief=tk.FLAT,
        )

        self.canvas = tk.Canvas(frm,
                                width=500,
                                height=500,
                                background=frm.cget('bg'),
                                highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        frm.grid_rowconfigure(0, weight=1)
        frm.grid_columnconfigure(0, weight=1)

        return frm

    def calculate_board_locations(self) -> None:
        """Calculates every coordinates needed, to use later on."""
        # Calculate cell locations
        self.loc_cen = [(0, 0) for _ in range(self.num_rows * self.num_cols)]
        self.coord_cells = [
            (0 for __ in range(6)) for _ in range(self.num_rows * self.num_cols)
        ]
        self.loc_circle = [
            (0, 0, 0, 0) for _ in range(self.num_rows * self.num_cols)
        ]
        cell_id = 0
        self.update_lengths()
        len_sq = self.cell_edge_length * math.sqrt(3) / 2
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                # Draw the cell.
                x = len_sq + row * len_sq + 2 * col * len_sq + self.CELL_PADDING
                y = 1.5 * row * self.cell_edge_length + self.CELL_PADDING
                loc = (
                    (x, y),  # top-middle
                    (x + len_sq, y + self.cell_edge_length * 0.5),  # top-right
                    (x + len_sq,
                     y + self.cell_edge_length * 1.5),  # bottom-right
                    (x, y + 2 * self.cell_edge_length),  # bottom-middle
                    (x - len_sq,
                     y + self.cell_edge_length * 1.5),  # bottom-left
                    (x - len_sq, y + self.cell_edge_length * 0.5),  # top-left
                )
                # Save the center of the cell.
                self.loc_circle[cell_id] = (
                    x - self.radius,
                    y + self.cell_edge_length - self.radius,
                    x + self.radius,
                    y + self.cell_edge_length + self.radius,
                )
                self.loc_cen[cell_id] = (x, y + self.cell_edge_length)
                # Save the cell coordinates.
                self.coord_cells[cell_id] = loc
                cell_id += 1

    def get_board_width(self) -> int:
        """Returns the width of the board_frame."""
        self.frame_board.update()
        board_width = self.frame_board.winfo_width()
        return board_width

    def get_board_height(self) -> int:
        """Returns the height of the board_frame."""
        self.frame_board.update()
        board_height = self.frame_board.winfo_height()
        return board_height

    def update_lengths(self) -> None:
        """Updates the lengths of the cells."""
        w = self.get_board_width() - self.CELL_PADDING * 2 - 8
        h = self.get_board_height() - self.CELL_PADDING * 2 - 8
        board_w = self.board_width_coefficient(self.num_rows, self.num_cols)
        board_h = self.board_height_coefficient(self.num_rows, self.num_cols)

        # board_size if we match board_w
        edge_len = w / board_w
        board_size = self.get_board_size(edge_len)
        if board_size[1] > h or board_size[0] > w:
            # board_size if we match board_h
            edge_len = h / board_h
            board_size = self.get_board_size(edge_len)
        self.cell_edge_length = edge_len
        self.radius = self.cell_edge_length / 2

    @staticmethod
    def board_width_coefficient(num_cols: int, num_rows: int) -> int:
        """Returns the width of the board."""
        return math.sqrt(3) * (num_cols + (num_rows - 1) / 2)

    @staticmethod
    def board_height_coefficient(num_cols: int, num_rows: int) -> int:
        """Returns the height of the board."""
        return num_rows * 1.5 + 0.5

    def get_board_size(self, edge_len: int) -> typing.Tuple[int, int]:
        """Returns the size of the board."""
        h = edge_len * self.board_height_coefficient(self.num_cols,
                                                     self.num_rows)
        w = edge_len * self.board_width_coefficient(self.num_cols,
                                                    self.num_rows)
        return (w, h)

    def save_file(self) -> None:
        """Saves the board to a file."""
        cur_dir = os.getcwd()
        path = tk.filedialog.asksaveasfilename(
            initialdir=cur_dir,
            title="Select a Folder",
            filetypes=(("all files", "*.*"), ("python files", "*.pkl")),
        )
        path = self._save_to(path)
        self.save_win.destroy()

    def save_file_default(self) -> None:
        """Saves the file to the default location."""
        # default location is data/nrxnc_new/game_info.pkl
        # find data
        pretty_time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        data_dir = os.path.join(
            os.path.dirname(__file__),
            f"tmp/strategy_data/{self.num_rows}x{self.num_cols}/{pretty_time}",
        )
        # create the directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        # save the file
        path = self._save_to(data_dir)
        self.save_win.destroy()

    def _save_to(self, path) -> str:
        data = {
            "num_cols": self.num_cols,
            "num_rows": self.num_rows,
            "player": self.player,
            "isomorphic": self.include_isomorphic,
            "initial_state": self.initial_state,
            "strategy": self.strat_gen.get_darkhex_policy(),
        }
        # save the file
        util.save_file(data, path + "/game_info.pkl")
        log.info(f"Saved the policy to {path}/game_info.pkl")
        return path


if __name__ == "__main__":
    app = PolicyGenGUI()
    app.mainloop()
