"""
Simple Hex Game GUI using pygame.

Primary development purpose is to use it for 
the strategy generator.
"""
import pygame
import pygame_textinput
import math
from darkhex.utils.convex import is_inside_polygon, is_inside_rectangle

class Colors:
    """RGB Colors used in the GUI."""
    cell_bg = (189, 105, 102)
    cell_hover = (196, 138, 135)
    player1_piece = (43, 34, 34)
    player1_lines = (10, 7, 7)
    player2_piece = (222, 209, 209)
    player2_lines = (153, 150, 150)
    line = (117, 13, 9)
    bg = (196, 175, 147)

    menu_bg =  (200, 200, 185)
    button_text = (48, 34, 24)
    button_bg = (194, 182, 174)
    button_hover = (143, 134, 129)
    button_click = (92, 88, 86)
    button_lines = (171, 153, 142)
    
    font_normal = (0, 0, 0)

class StrategyGeneratorGUI:
    """
    Hex Game Strategy Generator GUI.
    """
    def __init__(self, 
                 num_rows: int,
                 num_cols: int) -> None:
        """
        Initialize the GUI.
        """
        # Set the board size.
        self.num_rows = num_rows
        self.num_cols = num_cols

        # Initialize pygame.
        pygame.init()

        self.FPS = 60

        # Setup the stones properties.
        self.piece_size = 20

        # board margin setup
        self.TOP = 0
        self.BOTTOM = 1
        self.LEFT = 2
        self.RIGHT = 3
        self.board_margin = (50, 50, 50, 50) # top, bottom, left, right
        self.line_dist = 20

        # Setup menu
        self.menu_margin = (50, 50, 50, 50) # top, bottom, left, right
        self.button_bg = Colors.button_bg
        self.button_hover = Colors.button_hover
        self.button_click = Colors.button_click
        self.button_lines = Colors.button_lines
        self.button_text = Colors.button_text
        self.menu_height = 50
        self.menu_text_size = 20

        # Setup cell properties.
        self.cell_edge_len = 50
        self.sq_dist = self.cell_edge_len * math.sqrt(3) / 2
        self.line_width = 5
        self.cell_color = Colors.cell_bg

        self.sq_dist_wline = self.sq_dist - self.line_width

        # Set the background color.
        self.background_color = Colors.bg
        self.line_color = Colors.line
        
        even = (num_rows // 2)
        odd = (num_rows // 2) if (num_rows % 2 == 0) else (num_rows // 2) + 1
        vertical_size = odd * self.cell_edge_len + \
                        even * (2 * self.cell_edge_len)
        self.board_size = (self.board_margin[self.LEFT] + num_cols * self.sq_dist_wline * 2 + \
                           self.board_margin[self.RIGHT] + ((num_rows - 1) * self.sq_dist_wline),
                           self.board_margin[self.TOP] + vertical_size + \
                           self.board_margin[self.BOTTOM])
        self.board_pos = (0, 0)

        # Set the font.
        self.font = pygame.font.SysFont('Monospace', 20)

        # Set the font color.
        self.font_color = Colors.font_normal

        # Set the window size.
        self.gap_size = (50, 50)
        self.window_size = (self.board_size[0] + self.gap_size[0],
                            self.board_size[1] + self.gap_size[1] + self.menu_height)

        # Set the screen size.
        self.screen = pygame.display.set_mode(self.window_size)

        self.center_locations = [(0, 0) for _ in range(self.num_rows * self.num_cols)]
        self.cell_coordinates = [(0, 0, 0, 0, 0, 0) for _ in range(self.num_rows * self.num_cols)]
        self.line_locations = []

        self.board_info = [None for _ in range(self.num_rows * self.num_cols)]
        self.game_history = []

    def get_position(self, mouse_pos) -> int:
        """
        Get the cell id of the mouse position using the cell coordinates
        saved.
        """
        print(mouse_pos)
        for idx, cell in enumerate(self.cell_coordinates):
            if is_inside_polygon(cell, mouse_pos):
                return idx
        return -1

    def draw_piece(self, screen, cell_id, player) -> None:
        """
        Draw a stone.
        """
        # Get the piece color.
        if player == 0:
            piece_color = Colors.player1_piece
            line_color = Colors.player1_lines
        else:
            piece_color = Colors.player2_piece
            line_color = Colors.player2_lines

        # Draw the cell without hovering.
        self.draw_cell(screen, cell_id, False)
        
        # Draw the lines.
        pygame.draw.circle(screen,
                           line_color,
                           self.center_locations[cell_id],
                           self.piece_size + self.line_width)

        # Draw the piece.
        pygame.draw.circle(screen,
                           piece_color,
                           self.center_locations[cell_id],
                           self.piece_size)

        # Update board info
        self.board_info[cell_id] = player

    def draw_board(self, screen) -> None:
        """
        Draw the board.
        """
        # Draw the board.
        for cell_id in range(len(self.cell_coordinates)):
            self.draw_cell(screen, cell_id)
        
        # Add player lines.
        for loc in self.line_locations:
            pygame.draw.line(screen,
                             Colors.player1_lines if loc[2] == 0 else Colors.player2_lines,
                             loc[0],
                             loc[1],
                             self.line_width * 2)
  
    def draw_cell(self, screen, cell_id, hover_allowed=True) -> None:
        """
        Draws a hexagon cell with lines from the given location.
        """
        # Check if the cell is empty. If not don't draw it again.
        if self.board_info[cell_id] is not None:
            return

        mouse_loc = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]

        loc = self.cell_coordinates[cell_id]
        if is_inside_polygon(loc, mouse_loc) and hover_allowed:
            pygame.draw.polygon(screen, Colors.cell_hover, loc)
            if mouse_down:
                self.play_piece(cell_id, 0)
        else:
            pygame.draw.polygon(screen, self.cell_color, loc)
        

        # Draw the lines.
        for i in range(len(loc)):
            pygame.draw.line(screen,
                             self.line_color,
                             loc[i],
                             loc[(i + 1) % len(loc)],
                             self.line_width)

    def rewind(self):
        """Redraw the last cell in history (empty)."""
        if len(self.game_history) == 0:
            return
        cell_id = self.game_history.pop()
        self.board_info[cell_id] = None
        self.draw_cell(self.screen, cell_id)

    def restart(self):
        """Redraw the board and reset the game history."""
        self.game_history = []
        self.board_info = [None for _ in range(self.num_rows * self.num_cols)]
        self.draw_board(self.screen)

    def play_piece(self, cell_id, player):
        """
        Perform an action on the board.
        """
        self.game_history.append(cell_id)
        self.draw_piece(self.screen, cell_id, player)
        self.draw_board(self.screen)

    def draw_menu(self, screen) -> None:
        """
        Draw the menu.
        """
        loc = (0, self.window_size[1] - self.menu_height)
        pygame.draw.rect(screen,
                         Colors.menu_bg,
                         (loc[0], loc[1], self.window_size[0], self.menu_height))
    
        # Draw the menu buttons.
        num_buttons = 2
        button_height = self.menu_height
        button_width = self.window_size[0] // num_buttons
        self.draw_button(screen, loc, button_height, button_width, \
            "Rewind", self.rewind)
        self.draw_button(screen, (loc[0] + button_width, loc[1]), \
            button_height, button_width, "Restart", self.restart)

    def draw_button(self, screen, loc, h, w, text, action) -> None:
        """
        Draw a button.
        """
        mouse_loc = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]
        if is_inside_rectangle(*loc, w, h, mouse_loc):
            pygame.draw.rect(screen,
                             Colors.button_hover,
                             (loc[0], loc[1], w, h))
            if mouse_down:
                action()
        else:
            pygame.draw.rect(screen,
                             Colors.button_bg,
                             (loc[0], loc[1], w, h))
        # Draw the text.
        text_loc = (loc[0] + w // 2, loc[1] + h // 2)
        text_surface = self.font.render(text, True, self.font_color)
        text_rect = text_surface.get_rect()
        text_rect.center = text_loc
        screen.blit(text_surface, text_rect)

    def calculate_board_locations(self) -> None:
        """Calculates every coordinates needed, to use later on."""
        # Calculate cell locations
        cell_id = 0
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                # Draw the cell.
                left_dist = self.board_pos[0] + self.board_margin[self.LEFT] + \
                    self.sq_dist + row * (self.cell_edge_len - self.line_width)
                top_dist = self.board_pos[1] + self.board_margin[self.TOP]
                cell_location = (left_dist + 2 * col * self.sq_dist,
                                 top_dist + 1.5 * row * self.cell_edge_len)
                x = cell_location[0]
                y = cell_location[1]
                loc = (
                    (x, y), # top-middle
                    (x + self.sq_dist, y + self.cell_edge_len * .5), # top-right
                    (x + self.sq_dist, y + self.cell_edge_len * 1.5), # bottom-right
                    (x, y + 2 * self.cell_edge_len), # bottom-middle
                    (x - self.sq_dist, y + self.cell_edge_len * 1.5), # bottom-left
                    (x - self.sq_dist, y + self.cell_edge_len * .5), # top-left
                )
                # Save the center of the cell.
                self.center_locations[cell_id] = (x, y + self.cell_edge_len)
                # Save the cell coordinates.
                self.cell_coordinates[cell_id] = loc
                cell_id += 1

        for idx in range(self.num_cols):
            # first row
            loc = self.cell_coordinates[idx]
            self.line_locations.append(((loc[-1][0], loc[-1][1] - self.line_dist), (loc[0][0], loc[0][1] - self.line_dist), 0))
            self.line_locations.append(((loc[0][0], loc[0][1] - self.line_dist), (loc[1][0], loc[1][1] - self.line_dist), 0))
            # last row
            loc = self.cell_coordinates[idx + self.num_cols * (self.num_rows - 1)]
            self.line_locations.append(((loc[-2][0], loc[-2][1] + self.line_dist), (loc[-3][0], loc[-3][1] + self.line_dist), 0))
            self.line_locations.append(((loc[-3][0], loc[-3][1] + self.line_dist), (loc[-4][0], loc[-4][1] + self.line_dist), 0))
               
    def run(self) -> None:
        """
        Run the GUI.
        """
        # Set the window caption.
        pygame.display.set_caption('Hex Game')

        # Set the background color.
        self.screen.fill(self.background_color)

        # Update the screen.
        pygame.display.flip()

        # Calculate board locations.
        self.calculate_board_locations()

        # Set the clock.
        clock = pygame.time.Clock()

        # Loop until the user clicks the close button.
        done = False

        while not done:
            events = pygame.event.get()

            # Check for events.
            for event in events:
                if event.type == pygame.QUIT:
                    done = True

                # Draw the board.
                self.draw_board(self.screen)

                # Draw Menu.
                self.draw_menu(self.screen)

            # Limit to 60 frames per second.
            clock.tick(60)

            pygame.display.flip()

        # Close the window.
        pygame.quit()

def test_gui():
    """
    Test the GUI.
    """
    # Set the board size.
    num_rows = 3
    num_cols = 3

    # Initialize the GUI.
    gui = StrategyGeneratorGUI(num_rows, num_cols)

    # Run the GUI.
    gui.run()

if __name__ == '__main__':
    test_gui()