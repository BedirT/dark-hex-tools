import pyspiel
import os, psutil

def get_all_information_states(game: pyspiel.Game, include_terminal_states=True) -> list:
    """Get all information states for the given game."""
    info_states = {}
    state = game.new_initial_state()
    _get_all_info_states(state, info_states, include_terminal_states)
    process = psutil.Process(os.getpid())
    print(f"Total Memory used: {process.memory_info().rss / 1024 ** 2}")
    return info_states

def _get_all_info_states(state: pyspiel.State, info_states: dict,
                         include_terminal_states) -> None:
    """Calculate information states recursively for the state. Fill in the
    info_states."""
    process = psutil.Process(os.getpid())
    print(f"Total Memory used: {process.memory_info().rss / 1024 ** 2}", end="\r")
    r = -1
    if state.is_terminal():
        if include_terminal_states:
            r = 0 if state.returns()[0] > 0 else 1
        else:
            return
    info_tuple = (state.information_state_string(0),
                  state.information_state_string(1),)
    data = [(state.legal_actions(0), state.legal_actions(1)), r] 
                                    # if 0 its not a terminal state
    if info_tuple not in info_states:
        info_states[info_tuple] = data
    if state.is_terminal():
        return
    for action in state.legal_actions():
        new_state = state.child(action)
        _get_all_info_states(new_state, info_states, include_terminal_states)