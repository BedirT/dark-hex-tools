import numpy as np
from Projects.base.util.print_tools import seq_to_str
from Projects.base.game.darkHex import DarkHex
from Projects.base.game.hex import Hex, pieces
from tqdm import tqdm
from copy import deepcopy, copy
from collections import defaultdict
import pickle

class Node:
    def __init__(self, board, move_history, player, h, turn_num) -> None:
        self.player = player
        self.num_actions = len(board)
        self.move_history = move_history
        self.board = deepcopy(board)
        self.h = h
        self.turn_num = turn_num

        self.infoSet = get_infoset(self.board, self.h)

        self.strategy = np.zeros(self.num_actions)
        self.regretSum = np.zeros(self.num_actions)
        self.strategySum = np.zeros(self.num_actions)
        self.regrets = np.zeros(self.num_actions)

        self.T = 0
        self.u = 0
        self.pSum1 = 1
        self.pSum2 = 1
        self.visits = 1

        self.pos_actions = [i for i, x in enumerate(self.board) if x == pieces.kEmpty]

        self.is_terminal = False

        self.children = []
        self.parents = []

    def getStrategy(self): 
        normalizingSum = 0
        for a in self.pos_actions:
            self.strategy[a] = max(self.regretSum[a], 0)
            # * regret matching algorithm here.
            # * just use the positive regrets.
            normalizingSum += self.strategy[a]
            # Add all the positive regrets -> normSum
        for a in self.pos_actions:
            if normalizingSum > 0:
                # if normalizing sum was positive all the action probs will
                # be devided by normSum
                self.strategy[a] /= normalizingSum
            else:
                # otherwise all actions are equaprobable (random)
                self.strategy[a] = 1.0 / len(self.pos_actions)
            self.strategySum[a] += self.strategy[a] * (self.pSum1 if \
                    self.player == pieces.kBlack else self.pSum2)
            # * summing up all the action probabilities
            # ? what is realizationWeight again
        return self.strategy

    def getAverageStrategy(self):
        normalizingSum = 0
        for a in self.pos_actions:
            normalizingSum += self.strategySum[a]
            # summing up all the action probs using strategySum
            # ? why strategySum
        for a in self.pos_actions:
            if normalizingSum > 0:
                self.strategySum[a] /= normalizingSum
            else:
                self.strategySum[a] = 1 / len(self.pos_actions)
        return self.strategySum

    def update_infoset(self):
        self.infoSet = get_infoset(self.board, self.h)

    def __str__(self):
        return "{}:\t{}".format(self.infoSet, seq_to_str(self.getAverageStrategy(), spacing=' '))


class FSICFR:
    def __init__(self, num_rows=3, num_cols=3) -> None:
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_actions = num_cols * num_rows
        self.nodes, self.nodes_dict = self.__init_board_topSorted()

    def train(self, num_of_iterations) -> None:
        for it in tqdm(range(num_of_iterations)):
            for node in self.nodes: # top-sorted nodes
                if node.visits == 0:
                    node.visits = 1
                    node.pSum1 = 1 
                    node.pSum2 = 1
                rev_player = pieces.kBlack if node.player == pieces.kWhite else pieces.kWhite
                strategy = node.getStrategy()
                for a in node.pos_actions: 
                    # for each possible move
                    # take action a on board
                    children = []
                    # * update the board with action a and add the new
                    # * board state to the -children- to traverse later.
                    new_board = self.__placeStone(node.board, a, node.player)
                    children.append(get_infoset(new_board, node.h))
                    if node.h > 0:
                        new_board = self.__placeStone(node.board, a, rev_player)
                        children.append(get_infoset(new_board, node.h-1))
                    for infoset_c in children:
                        if infoset_c in self.nodes_dict:
                            # update visits
                            c = self.nodes_dict[infoset_c]
                            c.visits += node.visits
                            # update the rweights
                            c.pSum1 += (strategy[a] * node.pSum1 if node.player == pieces.kBlack else node.pSum1)
                            c.pSum2 += (strategy[a] * node.pSum2 if node.player == pieces.kWhite else node.pSum2)
                # endfor - pos_actions
            # endfor - nodes
            for node in self.nodes[::-1]:
                node.u = 0
                strategy = node.getStrategy()
                rev_player = pieces.kBlack if node.player == pieces.kWhite else pieces.kWhite
                game = Hex(BOARD_SIZE=[self.num_rows, self.num_cols],
                           BOARD=node.board, verbose=False)
                if game._game_status() == node.player:
                    node.u = 1
                elif game._game_status() != pieces.kDraw:
                    node.u = -1
                else:
                    for a in range(self.num_actions):
                        children = []
                        # * update the board with action a and add the new
                        # * board state to the -children- to traverse later
                        new_board = self.__placeStone(node.board, a, node.player)
                        if not new_board:
                            continue
                        children.append(get_infoset(new_board, node.h))
                        if node.h > 0:
                            new_board = self.__placeStone(node.board, a, rev_player)
                            if not new_board:
                                continue
                            children.append(get_infoset(new_board, node.h-1))
                        for _, infoset_c in enumerate(children):
                            if infoset_c in self.nodes_dict:
                                if self.nodes_dict[infoset_c].player == node.player:
                                    childUtil = self.nodes_dict[infoset_c].u
                                else:
                                    childUtil = - self.nodes_dict[infoset_c].u
                                node.regrets[a] += childUtil
                                node.u += strategy[a] * childUtil
                    cfp = node.pSum2 if node.player == pieces.kBlack else node.pSum1
                    for a in node.pos_actions:
                        nomin = (node.T * node.regretSum[a] + node.visits * cfp * (node.regrets[a] - node.u))
                        denom = node.T + node.visits
                        node.regretSum[a] = nomin / denom
                    node.T += node.visits

                node.visits = 0
                node.pSum1 = 0 
                node.pSum2 = 0
            
            # reset the strategysums - page 32
            if it == num_of_iterations//2:
                for node in self.nodes:
                    for a in range(len(node.strategySum)):
                        node.strategySum[a] = 0

        # for node in self.nodes:
        #     if not node.is_terminal:
        #         print(node.infoSet, node.getAverageStrategy())
                
    def __init_board_topSorted(self) -> list:
        # TODO: Remove more states using pONE
        stack = []; nodes_dict = {}; visited = defaultdict(lambda: False)
        game = DarkHex([self.num_rows, self.num_cols], False)

        # create a root node for graph representation
        root = Node(game.BOARD, [], pieces.kBlack, 0, 0)

        self.__topSort_play(game, root.infoSet, '=', stack, visited, nodes_dict)
        print("Phase 1 has ended...")
        print("{} number of unique states".format(len(nodes_dict)))

        # topologically sort the nodes_dict using childrens of indexes
        top_sorted = self.top_sort(nodes_dict)

        return top_sorted, nodes_dict

    def top_sort(self, nodes_dict: dict):
        '''
        Topologically sorting given dictionary based on child-parent
        relationship. Returns a list of nodes in topological order.
        '''
        for node in nodes_dict:
            for child in nodes_dict[node].children:
                nodes_dict[child.infoSet].parents.append(node)

        # sort the nodes based on the parents
        sorted_nodes = sorted(nodes_dict.values(), key=lambda x: len(x.parents))

        # reverse the list to get the top-sorted list
        nodes = sorted_nodes[::-1]
        # print nodes in order
        # for node in nodes:
        #     print(node.infoSet)

        return nodes

    def __topSort_play(self, game, root_info, res, stack, visited, nodes_dict) -> None:
        # player = game.turn_info
        player = game.turn_information_func()
        # * Given a game, return the top-sorted full states 
        # -------------------------------------------------
        # -> Create the node for the current game&player
        # -> Player plays every possible action
        # -> Call the next game
        # -> Save the infoSet + node
        ext_infoSet = tuple([*game.BOARDS[pieces.kBlack], *game.BOARDS[pieces.kWhite]])
        if res == pieces.kFail:
            node = Node(board=game.BOARDS[player], 
                        move_history=game.move_history[player],
                        player=player, 
                        h=game.hidden_stones_count(player),
                        turn_num=game.game_length)
            # ext_infoSet = get_infoset(node.board, node.h)
            if visited[ext_infoSet]:
                return 
            else:
                visited[ext_infoSet] = True
        else:
            # * CREATING THE NODE *********
            if res != pieces.kDraw:
                # If the game is over, switch player so
                # we get the ending players node
                player = res
            new_h = game.hidden_stones_count(player)
            node = Node(board=game.BOARDS[player], 
                        move_history=game.move_history[player],
                        player=player, 
                        h=new_h,
                        turn_num=game.game_length)                     
            node.is_terminal = res != pieces.kDraw
            # *******************************
            if visited[ext_infoSet]:
                return
            else:
                visited[ext_infoSet] = True

        if node.is_terminal:
            if node.infoSet not in nodes_dict:
                nodes_dict[node.infoSet] = node
                stack.append(node)
                nodes_dict[root_info].children.append(node)
                # root.children.append(node)
            return
             
        valid_moves = copy(game.valid_moves_colors[player])
        for a in valid_moves:
            _, res, _ = game.step(player, a)
            if node.infoSet not in nodes_dict:
                nodes_dict[node.infoSet] = node
                stack.append(node)
                if root_info != node.infoSet:
                    nodes_dict[root_info].children.append(node)
                    # root.children.append(node)
            self.__topSort_play(game, node.infoSet, res, stack, visited, nodes_dict)
            game.rewind(res == pieces.kFail)
            
        return

    def __placeStone(self, board, cell, color):
        '''
        Placing a stone on the board and returning the new board

        Args:
            board: current board
            cell: cell to place the stone on
            color: color of the stone

        Returns:
            new board
        '''
        new_board = deepcopy(board)
        # first check if the cell is empty
        # if not return False
        if new_board[cell] != pieces.kEmpty:
            return False
        if color == pieces.kBlack:
            north_connected = False
            south_connected = False 
            if cell < self.num_cols: # First row
                north_connected = True
            elif cell >= self.num_cols * (self.num_rows - 1): # Last row
                south_connected = True
            for neighbour in self._cell_connections(cell):
                if new_board[neighbour] == pieces.kBlackNorth:
                    north_connected = True
                elif new_board[neighbour] == pieces.kBlackSouth:
                    south_connected = True
            if north_connected and south_connected:
                new_board[cell] = pieces.kBlackWin
            elif north_connected:
                new_board[cell] = pieces.kBlackNorth
            elif south_connected:
                new_board[cell] = pieces.kBlackSouth
            else:
                new_board[cell] = pieces.kBlack
        elif color == pieces.kWhite:
            east_connected = False
            west_connected = False
            if cell % self.num_cols == 0: # First column
                west_connected = True
            elif cell % self.num_cols == self.num_cols - 1: # Last column
                east_connected = True
            for neighbour in self._cell_connections(cell):
                if new_board[neighbour] == pieces.kWhiteWest:
                    west_connected = True
                elif new_board[neighbour] == pieces.kWhiteEast:
                    east_connected = True
            if east_connected and west_connected:
                new_board[cell] = pieces.kWhiteWin
            elif east_connected:
                new_board[cell] = pieces.kWhiteEast
            elif west_connected:
                new_board[cell] = pieces.kWhiteWest
            else:
                new_board[cell] = pieces.kWhite
        if new_board[cell] in [pieces.kBlackWin, pieces.kWhiteWin]:
            return new_board
        elif new_board[cell] not in [pieces.kBlack, pieces.kWhite]:
            # The cell is connected to an edge but not a win position.
            # We need to use flood-fill to find the connected edges.
            flood_stack = [cell]
            latest_cell = 0
            while len(flood_stack) != 0:
                latest_cell = flood_stack.pop()
                for neighbour in self._cell_connections(latest_cell):
                    if new_board[neighbour] == color:
                        new_board[neighbour] = new_board[cell]
                        flood_stack.append(neighbour)
            # Flood-fill is complete.
        return new_board

    def _cell_connections(self, cell):
        '''
        Returns the neighbours of the given cell.

        args:
            cell    - The location on the board to check the neighboring cells for.
                    In the format [row, column]
        
        returns:
            format >> positions

            positions   - List of all the neighbouring cells to the cell.
                        Elements are in the format [row, column].
        '''
        # convert cell to row and column
        row = cell // self.num_cols
        col = cell % self.num_cols

        positions = []
        if col + 1 < self.num_cols:
            positions.append(self.__pos_by_coord(row, col + 1))
        if col - 1 >= 0:
            positions.append(self.__pos_by_coord(row, col - 1))
        if row + 1 < self.num_rows:
            positions.append(self.__pos_by_coord(row + 1, col))
            if col - 1 >= 0:
                positions.append(self.__pos_by_coord(row + 1, col - 1))
        if row - 1 >= 0:
            positions.append(self.__pos_by_coord(row - 1, col))
            if col + 1 < self.num_cols:
                positions.append(self.__pos_by_coord(row - 1, col + 1))
        return positions

    def __pos_by_coord(self, row, col):
        '''
        Returns the position of the given cell on the board.
        '''
        return row * self.num_cols + col

def get_infoset(board, h) -> tuple:
    return ''.join([*board, str(h)])

num_cols = 2
num_rows = 2
num_it = 1000

# UNCOMMENT - PHASE 1
cfr = FSICFR(num_cols=num_cols, num_rows=num_rows)

with open('ph1-cfr-{}x{}.pkl'.format(num_cols, num_rows), 'wb') as f:
    pickle.dump(cfr, f)

# # UNCOMMENT - PHASE 2
with open('ph1-cfr-{}x{}.pkl'.format(num_cols, num_rows), 'rb') as f:
    cfr = pickle.load(f)

cfr.train(num_it)

dct = {
    'nodes': cfr.nodes,
    'nodes_dict': cfr.nodes_dict
}

with open('results-{}x{}-{}it.pkl'.format(num_cols, num_rows, num_it), 'wb') as f:
    pickle.dump(dct, f)


print(len(dct['nodes_dict'].keys()))