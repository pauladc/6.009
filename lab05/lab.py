#!/usr/bin/env python3
"""6.009 Lab 5 -- Boolean satisfiability solving"""

import sys
import typing
import doctest
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS

def fibonacci_numbers(nums):
    x, y = 0, 1
    for _ in range(nums):
        x, y = y, x+y
        yield x

def square(nums):
    for num in nums:
        yield num**2

def all_bools(length):
    if length == 0:
        return [[]]
    else:
        out = []
        for v in all_bools(length-1):
            out.append([True] + v)
            out.append([False] + v)
        return out

def create_dict(formula, i=0, bool_dic={}):
    """
    Creates a dictionary containing all the variables in the formula
    """
    if isinstance(formula[0], tuple):
        for e in formula:
            bool_dic.update({e[0]: False})
    else:
        for i in range(len(formula)):
            try:
                create_dict(formula[i], i, bool_dic)
            except:
                pass
    return bool_dic

def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    variables = create_dict(formula)
    return variables


def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz room scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a list
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    raise NotImplementedError


if __name__ == '__main__':
    # import doctest
    # _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    # doctest.testmod(optionflags=_doctest_flags)
    print(create_dict([[('a', True), ('b', False), ('c', True)], [('d', False), ('g', False)], [('e', False)]]))
