"""Tourneyket
Easily represent and progress Bracket-style single elimination Tournaments,
allowing you to focus on matchup logic and analysis without worrying about the boilerplate. 

The Bracket object accepts an initial bracket and a function to select matchup winner.
Automatically fills out the rest of the bracket, and implements a method to print out the
final bracket to console in a nice, bracket shaped format. 
"""

from math import floor
from random import choice
from collections.abc import Callable

__author__ = "Shurjo Sakib Masood"
__copyright__ = "Copyright 2025, Shurjo Sakib Masood"
__license__ = "MIT"
__version__ = "0.1.5"
__email__ = "mail@shurjo.me"
__status__ = "Production"

def equal_chance(a: object, b: object) -> object:
    return choice([a, b]) 

class BracketError(Exception):
    pass

class Bracket():
    """
    Class used to represent a tree-style tournament bracket.
    Number of initial elements MUST be a power of 2. 

    ...

    Attributes
    -----------
    bracket : list 
        The full, played out bracket, in list form. 
        Each list element is a another list containing the participants of each successive round.
        Final list element a list with a single element, containing the ultimate winner. 

    first_round_size: int 
        The number of elements in the first round of the bracket, 
        i.e. the length of the initial bracket list passed to create a Bracket object

    Methods
    ----------
    play_out_bracket(function: pick_winner = equal_chance) -> None
        Plays out the bracket to completion, picking between two teams in a given matchup 
        using the function passed as the pick_winner parameter.
        Defaults to random (equal) chance.

    print_bracket(function: formatting = lambda t: t, int: spaces) -> None
        Prints out the bracket with in a bracket shape. 
        If the argument 'key' isn't passed, prints out each bracket element as is (in a bracket shape).

    """
    def __init__(self, initial_bracket: list, ) -> None:
        """
        Parameters
        -----------
        initial_bracket: list 
            A list of the initial bracket elements (first round competitors).
            MUST be of a length that is a power of 2.
            Needs to be ordered such that each matchup is next to each other.
            (i.e if first round is 1 v 4 and 2 v 3, and then second round between the winners of each matchup,
            the list must be in the order [1, 4, 2, 3])
            List elements can be of any type.

        Raises
        -------
        BracketError
            If the length of the initial bracket passed is not a power of 2
        """
        self.first_round_size = len(initial_bracket)
        if not ((self.first_round_size & (self.first_round_size - 1) == 0) and self.first_round_size != 0):
            raise BracketError("Starting bracket size is not a power of 2")
        self.bracket = [initial_bracket]

    def play_out_bracket(self, pick_winner: Callable[[object, object], object] = equal_chance) -> None:
        """
        Plays out the bracket to completion, picking between two teams in a given matchup 
        using the function passed as the pick_winner parameter.
        Defaults to random (equal) chance.

        Parameters 
        -----------
        pick_winner: function, optional 
            Function that takes 2 bracket elements and returns 1 bracket element (the winner of a matchup).
            (Default is equal_chance())
        """
        last_round_winners = list.copy(self.bracket[-1])
        while len(last_round_winners) > 1:
            i = 0 
            winners = []
            while i < (len(last_round_winners)):
                winners.append(pick_winner(last_round_winners[i], last_round_winners[i+1]))
                i += 2
            self.bracket.append(winners)
            last_round_winners = list.copy(winners)

    def _get_spacing(self, level: int) -> str:
        """
        Returns the first part of each printed string, i.e. the spacing string. 
        """
        if level == 0:
            return ""
        else:
            return (" " * self._spaces * (level - 1) + " |" + "-" * (self._spaces * 1 - 3) + " ")

    def _pivot(self, bracket: list, output_list: list, level: int) -> list:
        """
        Sets the string for the midpoint of the bracket, then breaks the bracket up into two halves
        and recursively calls itself. When the 'level' gets to 0, it just sets the midpoint and then returns.
        Returns a list of strings to be printed, in order.
        """
        midpoint_idx = floor(len(output_list)/2)
        team = self._formatting(bracket[level].pop(0))
        output_list[midpoint_idx] = "{}{}".format(self._get_spacing(level), team)
        if level > 0:
            output_list[:midpoint_idx] = self._pivot(bracket, [None] * len(output_list[:midpoint_idx]), level - 1)
            output_list[midpoint_idx+1:] = self._pivot(bracket, [None] * len(output_list[:midpoint_idx]), level -1)
        return output_list

    def print_bracket(self, formatting: Callable[[object], object] =lambda t: t, spaces: int = 20):
        """
        Prints out the bracket with in a bracket shape. 
        If the argument 'key' isn't passed, prints out each bracket element as is (in a bracket shape).

        Parameters 
        ----------
        key: function, optional
            Formatting for the bracket element string.
            (Default is just the element as is i.e. lambda t: t)

        spaces: int, optional
            Number of characters that separate the beginning of one round from the next.
            (Default is 20)
        """
        self._formatting = formatting
        self._spaces = spaces
        output_list = [None] * (self.first_round_size * 2 - 1)
        bracket_to_pop = list.copy(self.bracket)
        level = len(self.bracket) - 1
        output_list = self._pivot(bracket_to_pop, output_list, level)
        print("")
        for item in output_list:
            print(item)
        print("")
