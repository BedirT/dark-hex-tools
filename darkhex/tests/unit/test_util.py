import pytest
import darkhex.utils.util as util
from darkhex import cellState


def test_dotdict():
    d = util.dotdict({"a": 1, "b": 2})
    assert d.a == 1
    assert d.b == 2
    d.c = 3
    assert d.c == 3
    d.a = 4
    assert d.a == 4


def test_PathVars():
    assert util.PathVars.policies == "darkhex/data/policies/"
    assert util.PathVars.all_states == "darkhex/data/all_states/"
    assert util.PathVars.pone_states == "darkhex/data/pone_states/"
    assert util.PathVars.game_trees == "darkhex/data/game_trees/"


def test_neighbour_indexes():
    num_cols = 4
    num_rows = 3
    idx = 0
    assert set(util.neighbour_indexes(idx, num_cols, num_rows)) == set([1, 4])
    idx = 1
    assert set(util.neighbour_indexes(idx, num_cols,
                                      num_rows)) == set([0, 2, 4, 5])
    idx = 5
    assert set(util.neighbour_indexes(idx, num_cols,
                                      num_rows)) == set([1, 2, 4, 6, 8, 9])
    idx = 8
    assert set(util.neighbour_indexes(idx, num_cols,
                                      num_rows)) == set([4, 5, 9])
    idx = 10
    assert set(util.neighbour_indexes(idx, num_cols,
                                      num_rows)) == set([6, 7, 9, 11])
    idx = 11
    assert set(util.neighbour_indexes(idx, num_cols, num_rows)) == set([7, 10])


def test_board_after_action():
    num_rows = 3
    num_cols = 3
    board = "...\n...\n..."

    action = 0
    player = 0
    new_board = util.board_after_action(board, action, player, num_rows,
                                        num_cols)
    assert new_board == cellState.kBlack + board[1:]

    action = 1
    player = 0
    new_board = util.board_after_action(board, action, player, num_rows,
                                        num_cols)
    assert new_board == board[0] + cellState.kBlack + board[2:]

    action = 2
    player = 1
    new_board = util.board_after_action(board, action, player, num_rows,
                                        num_cols)
    assert new_board == board[0:2] + cellState.kWhite + board[3:]
    action = 1
    player = 1
    new_board = util.board_after_action(new_board, action, player, num_rows,
                                        num_cols)
    assert new_board == board[0:1] + cellState.kWhite * 2 + board[3:]


def test_convert_position_to_alphanumeric():
    num_cols = 4
    assert util.convert_position_to_alphanumeric(0, num_cols) == "a1"
    assert util.convert_position_to_alphanumeric(1, num_cols) == "b1"
    assert util.convert_position_to_alphanumeric(2, num_cols) == "c1"
    assert util.convert_position_to_alphanumeric(3, num_cols) == "d1"
    assert util.convert_position_to_alphanumeric(4, num_cols) == "a2"
    assert util.convert_position_to_alphanumeric(11, num_cols) == "d3"


def test_convert_alphanumeric_to_position():
    num_cols = 5
    assert util.convert_alphanumeric_to_position("a1", num_cols) == 0
    assert util.convert_alphanumeric_to_position("a2", num_cols) == 5
    assert util.convert_alphanumeric_to_position("d3", num_cols) == 13
    assert util.convert_alphanumeric_to_position("f4", num_cols) == False
    assert util.convert_alphanumeric_to_position("5", num_cols) == 5
    assert util.convert_alphanumeric_to_position("a", num_cols) == False


def test_convert_board_to_xo():
    board = "y..\n.x.\n..."
    assert util.convert_board_to_xo(board) == "x..\n.x.\n..."
    board = "y..\np.q\n.z."
    assert util.convert_board_to_xo(board) == "x..\no.o\n.x."


def test_convert_xo_to_board():
    board = "x..\n.x.\n..."
    assert util.convert_xo_to_board(board) == "y..\n.x.\n..."
    board = "x..\no.o\n.x."
    assert util.convert_xo_to_board(board) == "y..\np.q\n.z."
    board = "x..\nooo\n.x."
    assert util.convert_xo_to_board(board) == "y..\npOq\n.z."
    board = "xx.\noxo\n.x."
    assert util.convert_xo_to_board(board) == "yy.\npXq\n.z."
    board = "..x\n..o\n.ox\nox."
    assert util.convert_xo_to_board(board) == "..y\n..q\n.Oz\npz."


def test_is_collusion_possible():
    board = "x..\n.x.\n..."
    player = 0
    assert util.is_collusion_possible(board, player) == True
    board = "xo.\n.x.\n..."
    player = 1
    assert util.is_collusion_possible(board, player) == False
    board = "xoo\n.x.\n..."
    player = 0
    assert util.is_collusion_possible(board, player) == False


def test_is_board_terminal():
    board_in_xo = "x..\n.x.\n..."
    player = 0
    assert util.is_board_terminal(board_in_xo, player) == False
    board_in_xo = "ooo\n.x.\n.x."
    player = 0
    assert util.is_board_terminal(board_in_xo, player) == True
    board_connection = "y..\nX..\nz.."
    player = 0
    assert util.is_board_terminal(board_connection, player) == True
    board_incomplete = "o..\noo.\no.."
    player = 1
    assert util.is_board_terminal(board_incomplete, player) == True


def test_get_board_from_info_state():
    info_state = "P0\nx..\n.x.\n..."
    assert util.get_board_from_info_state(info_state) == "x..\n.x.\n..."
    info_state = "P0\nx..\n.x.\n...\n0, 0 0, 4"
    pr = True  # perfect recall
    assert util.get_board_from_info_state(info_state, pr) == "x..\n.x.\n..."


def test_get_imperfect_recall_state():
    board = "x..\n.x.\n..."
    player = 0
    assert util.get_imperfect_recall_state(player, board) == "P0\nx..\n.x.\n..."
    board = "oo.\n.x.\n..."
    player = 1
    assert util.get_imperfect_recall_state(player, board) == "P1\noo.\n.x.\n..."


def test_get_perfect_recall_state():
    board = "x..\n.x.\n..."
    player = 0
    action_history = [0, 4]
    assert util.get_perfect_recall_state(
        player, board, action_history) == "P0\nx..\n.x.\n...\n0, 0 0, 4 "
    board = "oo.\n.x.\n..."
    player = 1
    action_history = [0, 1, 4]
    assert util.get_perfect_recall_state(
        player, board, action_history) == "P1\noo.\n.x.\n...\n1, 0 1, 1 1, 4 "


def test_get_info_state_from_board():
    board = "x..\n.x.\n..."
    player = 0
    assert util.get_info_state_from_board(board, player) == "P0\nx..\n.x.\n..."
    board = "x..\n.x.\n..."
    pr = True  # perfect recall
    action_history = [0, 4]
    player = 0
    res = "P0\nx..\n.x.\n...\n0, 0 0, 4 "
    pr = True  # perfect recall
    assert util.get_info_state_from_board(board, player, action_history,
                                          pr) == res


def test_layered_board_to_flat():
    board = "x..\n.x.\n..."
    assert util.layered_board_to_flat(board) == "x...x...."
    board = "xox\n.x.\n..."
    assert util.layered_board_to_flat(board) == "xox.x...."
    board = "xox\n.x.\n...\noxx"
    assert util.layered_board_to_flat(board) == "xox.x....oxx"


def test_flat_board_to_layered():
    num_cols = 3
    board = "x...x...."
    assert util.flat_board_to_layered(board, num_cols) == "x..\n.x.\n..."
    board = "xox.x......"
    pytest.raises(AssertionError, util.flat_board_to_layered, board, num_cols)
    board = "xox.x....oxx"
    assert util.flat_board_to_layered(board, num_cols) == "xox\n.x.\n...\noxx"


def test_policy_dict_to_policy_tuple():
    test_policy = {
        "P0\n...\n...\n...": {
            0: 1.
        },
        "P0\nx..\n...\n...": {
            1: 0.5,
            2: 0.5
        },
        "P0\nxx.\n...\n...": {
            2: 1.
        },
    }  # ! Incomplete policy, just for testing
    tup_policy = util.policy_dict_to_policy_tuple(test_policy)
    assert isinstance(tup_policy["P0\n...\n...\n..."], list)
    assert isinstance(tup_policy["P0\n...\n...\n..."][0], tuple)
    assert tup_policy["P0\n...\n...\n..."][0] == (0, 1.)
    assert tup_policy["P0\nx..\n...\n..."][0] == (1, 0.5)


def test_policy_tuple_to_policy_dict():
    test_policy = {
        "P0\n...\n...\n...": [(0, 1.)],
        "P0\nx..\n...\n...": [(1, 0.5), (2, 0.5)],
        "P0\nxx.\n...\n...": [(2, 1.)],
    }  # ! Incomplete policy, just for testing
    dict_policy = util.policy_tuple_to_policy_dict(test_policy)
    assert dict_policy["P0\n...\n...\n..."] == {0: 1.}
    assert dict_policy["P0\nx..\n...\n..."] == {1: 0.5, 2: 0.5}
    assert dict_policy["P0\nxx.\n...\n..."] == {2: 1.}
