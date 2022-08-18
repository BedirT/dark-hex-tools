import tkinter as tk
import customtkinter as ctk
import math
from darkhex import cellState
import typing


class PolicyGenGUI(ctk.CTk):
    """ Using customtkinter grid system to create a GUI for the policy generator. """

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

        self.title("Policy Generator")
        self.setup_initial_variables()
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
        self.frame_right = ctk.CTkFrame(master=self,
                                        corner_radius=10)
        
        # Placing the frames on the grid
        self.frame_left.grid(row=0, column=0, sticky="nsew")
        self.frame_right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # ----- Layout arrangement: Filling the left frame -----
        # Left frame has 11x1 grid
        # All grids have weight 1 so we are not mentioning, except we fill the 
        # rows to create some gaps.
        self.frame_left.grid_rowconfigure(0, minsize=10)
        self.frame_left.grid_rowconfigure(1, minsize=40) # row 1 is for logo
        self.frame_left.grid_rowconfigure(5, weight=1)
        self.frame_left.grid_rowconfigure(11, minsize=10) # for the bottom gap

        self.setup_left_frame()

        # ----- Layout arrangement: Filling the right frame -----
        # Right frame has 2x2 grid
        self.frame_right.grid_columnconfigure(0, weight=1, minsize=self.LOG_WIDTH)
        self.frame_right.grid_columnconfigure(1, weight=10, minsize=self.BOARD_WIDTH)
        self.frame_right.grid_rowconfigure(0, weight=1)
        self.frame_right.grid_rowconfigure(1, weight=3)

        self.setup_history_frame()
        self.setup_log_frame()
        self.setup_board_frame()
        self.setup_actions_frame()

        self.setup_right_frame()

        self.draw_board('.........')
        self.setup_bindings()

        # set default values
        self.menu_appearance.set("Dark")

    def setup_bindings(self):
        # ctrl + d to exit
        self.bind("<Control-d>", self.on_closing)
        # ctrl + n to create a new policy
        self.bind("<Control-n>", self.on_new_policy)
        # ctrl + o to open a policy (load)
        self.bind("<Control-o>", self.on_load_policy)
        # alt + r for random action
        self.bind("<Alt-r>", self.random_action)
        # ctrl + z for rewind
        self.bind("<Control-z>", self.rewind_action)
        # ctrl + r for reloading the board
        self.bind("<Control-r>", self.reload_board)

    def reload_board(self, event):
        self.frame_board.update_idletasks()
        self.draw_board(self.state)

    def setup_initial_variables(self):
        """ Sets up the initial variables. """
        self.num_cols = 3
        self.num_rows = 3
        self.state = '.........'
        self.last_size = [0, 0]

    def setup_left_frame(self):
        # create the items
        self.label_logo = ctk.CTkLabel(master=self.frame_left,
                                       text="PolGen",
                                       text_font=self.FONT_LOGO)
        self.button_new_policy = ctk.CTkButton(master=self.frame_left,
                                        text="New Policy",
                                        text_font=self.FONT_BUTTON,
                                        command=self.on_new_policy)
        self.button_load_policy = ctk.CTkButton(master=self.frame_left,
                                        text="Load Policy",
                                        text_font=self.FONT_BUTTON,
                                        command=self.on_load_policy)
        self.label_ap_mode = ctk.CTkLabel(master=self.frame_left, 
                                          text="Appearance Mode:",
                                          justify=tk.LEFT,
                                          anchor=tk.S,)
        self.menu_appearance = ctk.CTkOptionMenu(master=self.frame_left,
                                                 values=["Light", "Dark", "System"],
                                                 command=self.change_appearance_mode)
        self.label_credit = ctk.CTkLabel(master=self.frame_left,
                                         text="Created by Bedir Tapkan",
                                         text_font=self.FONT_LABEL,
                                         justify=tk.CENTER,
                                         text_color="grey")
        
        # place the items
        self.label_logo.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.button_new_policy.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.button_load_policy.grid(row=3, column=0, sticky="nsew", padx=20, pady=10)
        self.label_ap_mode.grid(row=8, column=0, sticky="nse", padx=20, pady=(10, 3))
        self.menu_appearance.grid(row=9, column=0, sticky="nsew", padx=20, pady=(0, 5))
        self.label_credit.grid(row=10, column=0, sticky="nsew", padx=20, pady=5)

    def setup_history_frame(self):
        self.frame_info_state_history = ctk.CTkFrame(master=self.frame_right)
        self.frame_info_state_history.rowconfigure(1, weight=1)
        self.frame_info_state_history.columnconfigure(0, weight=1)
        # creating the items for subframes
        self.label_info_state_history = ctk.CTkLabel(master=self.frame_info_state_history,
                                                    text="Information State History:",
                                                    text_font=self.FONT_LABEL,
                                                    justify=tk.LEFT,
                                                    anchor=tk.NW)
        self.text_info_state_history = tk.Text(master=self.frame_info_state_history,
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
        self.scrollbar_info_state_history = ctk.CTkScrollbar(master=self.frame_info_state_history,
                                                            command=self.text_info_state_history.yview)
        self.text_info_state_history.configure(yscrollcommand=self.scrollbar_info_state_history.set)

        # placing the items on subframes
        self.label_info_state_history.grid(row=0, column=0, sticky="nwes", padx=10, pady=(10,0))
        self.text_info_state_history.grid(row=1, column=0, sticky="news", padx=10, pady=(0,10))

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
        self.label_logs.grid(row=0, column=0, sticky="nwes", padx=10, pady=(10,0))
        self.text_logs.grid(row=1, column=0, sticky="news", padx=10, pady=(0,10))

    def setup_board_frame(self):
        """ Sets up the board frame """
        self.frame_board = self._init_board_frame()

        self.frame_board.update()
        canvas_width = self.frame_board.winfo_width()
        canvas_height = self.frame_board.winfo_height()  
        print(canvas_width, canvas_height)

        # Frame board is 1x1 grid
        self.frame_board.rowconfigure(0, weight=1)
        self.frame_board.columnconfigure(0, weight=1)

    def setup_actions_frame(self):
        # Frame actions is 3x4 grid
        self.frame_actions = ctk.CTkFrame(master=self.frame_right)
        self.frame_actions.rowconfigure((0,1,2), weight=1)
        self.frame_actions.columnconfigure((0,1,2), weight=1)

        # creating the widgets for the actions frame
        self.label_current_info_state_title = ctk.CTkLabel(master=self.frame_actions,
                                                           text="Current Info State:",
                                                           justify=tk.RIGHT,
                                                           anchor=tk.E,)
        self.label_current_info_state = ctk.CTkLabel(master=self.frame_actions,
                                                     text="P0 ............",
                                                     justify=tk.LEFT)
        self.entry_action_probs = ctk.CTkEntry(master=self.frame_actions,
                                                       placeholder_text="Next Action Probabilities...",)
        self.button_random = ctk.CTkButton(master=self.frame_actions,
                                           text="Random",
                                           command=self.random_action) # todo: change with an icon instead
        self.button_rewind = ctk.CTkButton(master=self.frame_actions,
                                           text="Rewind",
                                           command=self.rewind_action) # todo: change with an icon instead
        self.button_restart = ctk.CTkButton(master=self.frame_actions,
                                           text="Restart",
                                           fg_color=self.COLORS["red"],
                                           hover_color=self.COLORS["red_hover"],
                                           command=self.restart_game) # todo: change with an icon instead

        # placing the items on the actions frame
        self.label_current_info_state_title.grid(row=0, column=0, sticky="nes", padx=10, pady=(10,0))
        self.label_current_info_state.grid(row=0, column=1, columnspan=2, sticky="nws", padx=10, pady=(10,0))
        self.entry_action_probs.grid(row=1, column=0, columnspan=4, sticky="news", padx=10, pady=(0,10))
        self.button_random.grid(row=2, column=0, sticky="news", padx=10, pady=(0,10))
        self.button_rewind.grid(row=2, column=1, sticky="news", padx=10, pady=(0,10))
        self.button_restart.grid(row=2, column=2, sticky="news", padx=10, pady=(0,10))

    def setup_right_frame(self):
        """ Placing the items on the right frame """
        self.frame_info_state_history.grid(row=0, column=0, sticky="nsew", padx=(10, 10), pady=(10, 10))
        self.frame_logs.grid(row=1, column=0, sticky="nsew", padx=(10, 10), pady=(0, 10))

        self.frame_board.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=(10, 10), ipadx=10, ipady=10)
        self.frame_actions.grid(row=1, column=1, sticky="nsew", padx=(0, 10), pady=(0, 10))

    def on_new_policy(self):
        """ Creates a new policy. """
        pass

    def on_load_policy(self):
        """ Loads a policy. """
        pass

    def on_closing(self):
        """ Closes the window. """
        self.destroy()

    def change_appearance_mode(self, new_appearance_mode):
        """ Changes the appearance mode. """
        ctk.set_appearance_mode(new_appearance_mode)

    def random_action(self):
        """ Randomly selects an action. """
        pass

    def rewind_action(self):
        """ Rewinds the game. """
        pass

    def restart_game(self):
        """ Restarts the game. """
        pass

    def draw_board(self, board_str: str) -> None:
        self.canvas.delete("all")
        self.calculate_board_locations()
        for cell_id in range(self.num_rows * self.num_cols):
            self._draw_cell(board_str[cell_id], cell_id)

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
        text_id = chr(ord("a") + cell_id % self.num_cols) + str(cell_id // self.num_cols +
                                                          1)
        self.canvas.create_text(self.loc_cen[cell_id],
                                text=str(text_id),
                                fill=self.COLORS["white"])

    def _init_board_frame(self) -> tk.Frame:
        frm = ctk.CTkFrame(
            master=self.frame_right,
            pady=10, 
            padx=10,
            relief=tk.FLAT,)

        self.canvas = tk.Canvas(frm, width=500, height=500, 
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
        self.loc_circle = [(0, 0, 0, 0) for _ in range(self.num_rows * self.num_cols)]
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
                    (x + len_sq, y + self.cell_edge_length * 1.5),  # bottom-right
                    (x, y + 2 * self.cell_edge_length),  # bottom-middle
                    (x - len_sq, y + self.cell_edge_length * 1.5),  # bottom-left
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
        return math.sqrt(3) * (num_cols + (num_rows-1)/2)

    @staticmethod
    def board_height_coefficient(num_cols: int, num_rows: int) -> int:
        """Returns the height of the board."""
        return num_rows * 1.5 + 0.5

    def get_board_size(self, edge_len: int) -> typing.Tuple[int, int]:
        """Returns the size of the board."""
        h = edge_len * self.board_height_coefficient(self.num_cols, self.num_rows)
        w = edge_len * self.board_width_coefficient(self.num_cols, self.num_rows)
        return (w, h)


if __name__ == "__main__":
    app = PolicyGenGUI()
    app.mainloop()
