import pyspiel
import pickle as pkl
from darkhex.utils.util import save_file
import time

# todo: use file version if exists
# todo: make dumping to file optional

def get_all_information_states(game: pyspiel.Game,
                               include_terminal_states=True,
                               save_to_file=False,
                               get_data=True) -> list:
    """Get all information states for the given game."""
    info_states = {}
    state_data = {}
    state = game.new_initial_state()

    start = time.time()
    _get_all_info_states(state, info_states, state_data,
                         include_terminal_states)
    if get_data:
        _get_all_info_states_data(state, info_states, state_data,
                                  include_terminal_states)
        return_data = [info_states, state_data]
    else:
        _get_all_info_states(state, info_states, state_data,
                             include_terminal_states)
        return_data = state_data
    if save_to_file:
        data = {
            'state_data': state_data,
            'info_states': info_states,
            'len': len(info_states),
            'time_to_cal': time.time() - start,
        }
        save_file(data, f"darkhex/data/state_data/{game}.pkl")
    print(f'Number of states: {len(state_data)}')
    return return_data


def _get_all_info_states_data(state: pyspiel.State, info_states: dict,
                              state_data: dict,
                              include_terminal_states) -> None:
    """Calculate information states recursively for the state. Fill in the
    info_states and state_data."""
    r = -1
    print(f"Len: {len(state_data)}", end='\r')
    if state.is_terminal():
        if include_terminal_states:
            r = 0 if state.returns()[0] > 0 else 1
        else:
            return
    info_tuple = (
        state.information_state_string(0),
        state.information_state_string(1),
    )
    data = [(state.legal_actions(0), state.legal_actions(1)), r]
    # if 0 its not a terminal state
    if info_tuple not in info_states:
        info_states[info_tuple] = data
        if not state.is_terminal():
            if state.information_state_string(
                    state.current_player()) not in state_data:
                state_data[state.information_state_string(
                    state.current_player())] = state
    else:
        return
    if state.is_terminal():
        return
    for action in state.legal_actions():
        new_state = state.child(action)
        _get_all_info_states(new_state, info_states, state_data,
                             include_terminal_states)


def _get_all_info_states_to_count(state: pyspiel.State,
                                  info_states: dict) -> None:
    """Calculate information states recursively for the state. Fill in the
    info_states."""
    print(f"Len: {len(info_states)}", end='\r')
    if state.is_terminal():
        return
    info_state_str = state.information_state_string()
    if info_state_str not in info_states:
        info_states[info_state_str] = state
    for action in state.legal_actions():
        new_state = state.child(action)
        _get_all_info_states_to_count(new_state, info_states)


def _get_all_info_states(state: pyspiel.State, oracle: dict, state_data: dict,
                         include_terminal_states: bool) -> None:
    """Calculate information states recursively for the state. Fill in the
    state_data."""
    print(f'Number of states: {len(state_data)}', end='\r')
    if state.is_terminal() and not include_terminal_states:
        return
    info_tuple = (
        state.information_state_string(0),
        state.information_state_string(1),
    )
    if info_tuple in oracle:
        return
    oracle[info_tuple] = True
    cur_player = state.current_player()
    if cur_player < 0:
        cur_player = 0 if state.returns()[0] > 0 else 1
    cur_is = state.information_state_string(cur_player)
    if cur_is not in state_data:
        state_data[cur_is] = state
    for action in state.legal_actions():
        new_state = state.child(action)
        _get_all_info_states(new_state, oracle, state_data,
                             include_terminal_states)


if __name__ == "__main__":
    data = get_all_information_states(pyspiel.load_game("phantom_ttt_ir"), save_to_file=True)
