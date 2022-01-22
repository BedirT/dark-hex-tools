"""Strategy generator app with Tkinter GUI."""
from ast import arg
import tkinter as tk
import math
from tkinter import Grid, font

init_board = '...x........'
nr = 3
nc = 4
len_ce = 70 # length of cell edge
r = 35 # radius of circle

colors = {
    'black': '#000000',
    'white': '#ffffff',
    # (189, 105, 102)
    '.': '#bd6966',
    'x': '#2b2222',
    'o': '#c7b6a3',
    'btn_txt': '#9bbede',
    'btn_bg': '#06192b',
}

class StrategyGenerator:
    def __init__(self) -> None:
        self.root = tk.Tk()
        # Set the title of the window.
        self.root.title("Strategy Generator")

        # Set the window unresizable.
        self.root.resizable(False, False)

        # Configure the row and columns
        Grid.rowconfigure(self.root, 0, weight=1)
        Grid.columnconfigure(self.root, 0, weight=1)

        self.frm_board = self.init_board_frame()
        self.frm_board.grid(row=0, column=0, sticky='nsew')

        self.frm_menu_bar = self.init_menu_frame()
        self.frm_menu_bar.grid(row=1, column=0, sticky='nsew')

        self.frm_input_bar = self.init_input_frame()
        self.frm_input_bar.grid(row=2, column=0, sticky='nsew')

        self.root.mainloop()

    def init_menu_frame(self) -> tk.Frame:
        frm = tk.Frame(padx=10, pady=10)
        
        # Add a button to the frame
        btn_rewind = tk.Button(frm, text="Rewind", command=self.rewind, height=2,
                               font='Helvetica 14 bold')
        btn_restart = tk.Button(frm, text="Restart", command=self.restart, height=2,
                                font='Helvetica 14 bold')
        btn_rewind.grid(row=0, column=0, sticky='nsew')
        btn_restart.grid(row=0, column=1, sticky='nsew')
        Grid.columnconfigure(frm, 0, weight=1)
        Grid.columnconfigure(frm, 1, weight=1)

        return frm

    def init_input_frame(self) -> tk.Frame:
        frm = tk.Frame(padx=10, pady=10)
        
        # Add a label to the frame
        lbl_input = tk.Label(frm, text="Input:", font='Helvetica 14 bold')
        lbl_input.grid(row=0, column=0, sticky='nsew')
        # Input field.
        self.ent_input = tk.Entry(frm, font='Helvetica 14')
        self.ent_input.grid(row=0, column=1, sticky='nsew')

        # Add a button to the frame
        btn_submit = tk.Button(frm, text="Enter", command=self.enter, height=2,
                                 font='Helvetica 14 bold', padx=20)
        btn_submit.grid(row=0, column=2, sticky='e')

        Grid.columnconfigure(frm, 0, weight=1)
        Grid.columnconfigure(frm, 1, weight=7)
        Grid.columnconfigure(frm, 2, weight=1)
        Grid.rowconfigure(frm, 0, weight=1)

        return frm

    def init_board_frame(self) -> tk.Frame:
        self.loc_cen = [(0, 0) for _ in range(nr * nc)]
        self.coord_cells = [(0 for __ in range(6)) for _ in range(nr * nc)]
        self.loc_circle = [(0, 0, 0, 0) for _ in range(nr * nc)]
        self.calculate_board_locations()
        
        frm = tk.Frame(pady=20, padx=20)
        frm.configure(background='#1f1f1f')
        
        canvas_width = self.coord_cells[-1][1][0] - self.coord_cells[0][-1][0]
        canvas_height = self.coord_cells[-1][3][1] - self.coord_cells[0][0][1]

        self.canvas = tk.Canvas(frm, width=canvas_width, height=canvas_height)
        self.canvas.configure(background='#1a1a1a')
        self.canvas.grid(row=0, column=0, sticky='nsew')

        frm.grid_rowconfigure(0, weight=1)
        frm.grid_columnconfigure(0, weight=1)

        self.draw_board(init_board)

        return frm

    def calculate_board_locations(self) -> None:
        """Calculates every coordinates needed, to use later on."""
        # Calculate cell locations
        cell_id = 0
        len_sq = len_ce * math.sqrt(3) / 2
        for row in range(nr):
            for col in range(nc):
                # Draw the cell.
                x = len_sq + row * len_sq + 2 * col * len_sq
                y = 1.5 * row * len_ce
                loc = (
                    (x, y), # top-middle
                    (x + len_sq, y + len_ce * .5), # top-right
                    (x + len_sq, y + len_ce * 1.5), # bottom-right
                    (x, y + 2 * len_ce), # bottom-middle
                    (x - len_sq, y + len_ce * 1.5), # bottom-left
                    (x - len_sq, y + len_ce * .5), # top-left
                )
                # Save the center of the cell.
                self.loc_circle[cell_id] = (x - r, y + len_ce - r, x + r, y + len_ce + r)
                self.loc_cen[cell_id] = (x, y + len_ce)
                # Save the cell coordinates.
                self.coord_cells[cell_id] = loc
                cell_id += 1

    def draw_board(self, board_str: str) -> None:
        self.canvas.delete('all')
        for cell_id in range(nr * nc):
            self.draw_cell(board_str[cell_id], cell_id)
        
    def draw_cell(self, cell_str: str, cell_id: int) -> None:
        """Draws a cell on the canvas."""
        # Draw the cell.
        self.canvas.create_polygon(self.coord_cells[cell_id],
                                   fill=colors['.'],
                                   outline=colors['black'],
                                   width=4)
        # Draw the cell's content.
        if cell_str == 'x':
            self.canvas.create_oval(self.loc_circle[cell_id],
                                    fill=colors['x'],
                                    outline=colors['black'],
                                    width=4)
        elif cell_str == 'o':
            self.canvas.create_oval(self.loc_circle[cell_id],
                                    fill=colors['o'],
                                    outline=colors['black'],
                                    width=4)
        # Draw the cell id.
        self.canvas.create_text(self.loc_cen[cell_id],
                                text=str(cell_id),
                                fill=colors['white'])

    def enter(self) -> None:
        print("Entered:", self.ent_input.get())
        self.ent_input.delete(0, 'end')

    def rewind(self) -> None:
        print("Rewind")

    def restart(self) -> None:
        print("Restart")

if __name__ == "__main__":
    StrategyGenerator()