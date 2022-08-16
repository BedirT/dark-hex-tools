import typing
import pickle
import numpy as np
import pyspiel
import darkhex.policy as DarkhexPolicy
import darkhex.utils.util as util
from darkhex import *


def calculate_fractions(frac_limit: int) -> typing.Set[float]:
    """
    Calculate the fraction values to consider. Starts with 1/1 and
    goes by incrementing the denominator by 1 until the frac_limit
    and adding all the simple fractions to the set.

    Args:
        frac_limit (int): The maximum denominator to consider.
        
    Returns:
        typing.Set[float]: The set of fractions.
    """
    fractions = set()
    for n in range(1, frac_limit + 1):
        for k in range(1, n):
            frac = k / n
            fractions.add(frac)
    return sorted(fractions)


class SimPly:  # Simplified Policy
    """
    Simplified Policy algorithm as introduced in SIMCAP and SIMCAP+ from my thesis.
    included 4 parameters:
        - epsilon: the minimum probability of an action to be considered
        - max_number_of_actions: the maximum number of actions to consider
    Plus:
        - eta: the maximum difference between an action probability and a fraction
        - fraction_values: the fraction values to consider
    This is a post-processing algorithm that must be applied on top of an existing
    policy.
    """

    def __init__(
        self,
        policy: DarkhexPolicy.Policy,
        player: int,
        epsilon: float,
        action_cap: int,
        eta: float,
        frac_limit: int,
    ):
        """
        Initialize the policy simplification algorithm.
        
        Args:
            policy (Policy): The policy to apply SimPly on.
            player (int): The player to generate the simplified policy for.
            epsilon (float): The minimum probability of an action to be considered.
            action_cap (int): The maximum number of actions.
            eta (float): The maximum distance between a fraction and an action.
            frac_limit (int): The maximum number of fractions.
        """
        self.policy = policy
        self.player = player
        self._action_cap = action_cap
        self._epsilon = epsilon
        self._frac_limit = frac_limit
        self._eta = eta

        self.fraction_values = None
        if self._eta > 0 and self._frac_limit > 0:
            self.fraction_values = calculate_fractions(self._frac_limit)

        algo_name = "SimPly" if self._eta == 0 and self._frac_limit == 0 else "SimPly+"
        logger.info(f"Running {algo_name} with parameters---[epsilon:{self._epsilon},"+
        f"action_cap:{self._action_cap},eta:{self._eta},frac_limit:{self._frac_limit}]")

        self.all_states = get_all_states(self.policy.board_size)
        self.new_policy = {}

        logger.info(f"Generating the {algo_name} policy...")
        self._iterate_info_state(self.policy.initial_state)

    def _iterate_info_state(self, info_state: str) -> None:
        """
        Iterate the information state and update the info_set as to have the new
        policy. This is done by setting all the possible states for the
        continuation of the current state and then finding the action probabilities
        for each state based on the parameters and the existing policy.
        This is a recursive function, filling the info_set with all the
        possible states and action probabilities.

        Args:
            info_state (str): The info_state to iterate.
        """
        new_info_states = self._get_new_info_states(info_state)
        if not new_info_states:
            return
        actions = self.new_policy[info_state].keys()
        collusion_possible = util.is_collusion_possible(info_state, self.player)
        for action in actions:
            new_info_state = new_info_states[f"{action}{self.player}"]
            if not util.is_board_terminal(new_info_state, self.player) and \
               new_info_state not in self.new_policy:
                self._iterate_info_state(new_info_state)
            if collusion_possible:
                new_info_state = new_info_states[
                    f"{action}{self.policy.opponent}"]
                if not util.is_board_terminal(new_info_state, self.player) and \
                   new_info_state not in self.new_policy:
                    self._iterate_info_state(new_info_state)

    def _get_new_info_states(self, info_state: str) -> typing.Dict[str, str]:
        """
        Get new information states after the given info_state.

        Args:
            info_state (str): The current info_state.
        
        Returns:
            typing.Dict[str, str]: The new information states.
        """
        action_probs = self._get_action_probs(info_state)
        if action_probs is None:
            return {}
        action_probs = self._fractionize(action_probs)
        self.new_policy[info_state] = action_probs
        new_info_states = {}
        for a in self.new_policy[info_state].keys():
            info_state_board = util.get_board_from_info_state(info_state)
            new_board_collision = util.board_after_action(
                info_state_board, a, 1-self.player, self.policy.num_rows, self.policy.num_cols)
            new_info_state_collision = util.get_info_state_from_board(new_board_collision, self.player) 
            new_board = util.board_after_action(new_info_state_collision, a, self.player,
                                                self.policy.num_rows, self.policy.num_cols)
            new_info_state = util.get_info_state_from_board(new_board, self.player)
            if new_info_state_collision:
                new_info_states[
                    f"{a}{1-self.player}"] = new_info_state_collision
            if new_info_state:
                new_info_states[f"{a}{self.player}"] = new_info_state
        return new_info_states

    def _get_action_probs(self, info_state: str) -> typing.Dict[str, float]:
        """
        Get action probabilities for the information state using the policy and 
        the parameters.
        
        Args:
            info_state (str): The info_state to get the action probabilities for.
        
        Returns:
            typing.Dict[str, float]: The action probabilities for the
            information state
        """
        pyspiel_state = self._state_for_info_state(info_state)
        if pyspiel_state is None:
            return None
        action_probs_init = self.policy.get_action_probabilities(pyspiel_state)
        # only n actions per state is possible, so keep max n
        # actions and their probabilities, and renormalize the probabilities
        # to sum to 1. All actions must have probabilities greater than epsilon
        # to be considered.
        legal_actions = pyspiel_state.legal_actions(self.player)
        action_probs = {
            i: action_probs_init[i]
            for i in legal_actions
            if action_probs_init[i] > self._epsilon
        }
        if not action_probs:
            # No actions larger than epsilon
            # Choose a single action with the highest probability
            pos_actions = [
                i for i in legal_actions
                if action_probs_init[i] == max(action_probs_init.values())
            ]
            action = np.random.choice(pos_actions)
            action_probs = {action: 1.0}
        sorted_action_probs = sorted(action_probs.items(),
                                     key=lambda x: x[1],
                                     reverse=True)
        sorted_action_probs = sorted_action_probs[:self._action_cap]
        action_probs = {k: v for k, v in sorted_action_probs}
        total = sum(action_probs.values())
        action_probs = {k: v / total for k, v in action_probs.items()}
        return action_probs

    def _fractionize(
            self, action_probs: typing.Dict[str,
                                            float]) -> typing.Dict[str, float]:
        """
        Fractionize the action probabilities.

        For a given action probability, find if "all" action probabilities
        are within eta distance of a fraction value. If so, return the
        fraction values. If not, return the original action probabilities.

        Args:
            action_probs (typing.Dict[str, float]): The action probabilities to _fractionize.

        Returns:
            typing.Dict[str, float]: The fractionized action probabilities.
        """
        if not self.fraction_values:
            return action_probs
        fraction_probs = {}
        for action, prob in action_probs.items():
            for frac in self.fraction_values:
                if abs(frac - prob) <= self._eta:
                    if action not in fraction_probs:
                        fraction_probs[action] = frac
                    else:
                        # if the fraction is already in the dict,
                        # get the closest fraction value
                        if abs(prob - fraction_probs[action]) > \
                           abs(prob - frac):
                            fraction_probs[action] = frac
        if len(fraction_probs) == len(action_probs):
            if sum(fraction_probs.values()) == 1:
                return fraction_probs
        return action_probs

    def _state_for_info_state(self, info_state: str) -> pyspiel.State:
        return None if info_state not in self.all_states else self.all_states[
            info_state]

    def save_policy(self, policy_name: str) -> None:
        """
        Creates a new darkhex policy and saves it to the policy directory with
        the given policy name.

        Args:
            policy_name (str): The name of the policy to save.
        """
        policy = DarkhexPolicy.SinglePlayerTabularPolicy(
            self.new_policy, self.policy.board_size, self.policy.initial_state, self.player)
        policy.save_policy_to_file(policy_name)
