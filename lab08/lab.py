#!/usr/bin/env python3
"""6.009 Lab 8: Carlae (LISP) Interpreter"""

from ast import arguments
import doctest

# NO ADDITIONAL IMPORTS!


###########################
# Carlae-related Exceptions #
###########################


class CarlaeError(Exception):
    """
    A type of exception to be raised if there is an error with a Carlae
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class CarlaeSyntaxError(CarlaeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class CarlaeNameError(CarlaeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class CarlaeEvaluationError(CarlaeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    CarlaeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(x):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return x


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Carlae
                      expression
    """
    
    def separate_item(src, new_lst):
        try:
            if ')' in src[0] or '(' in src[0]:
                new_lst.append(src[0])
                separate_item(src[1:], new_lst)
            elif ')' in src[-1] or '(' in src[-1]:
                separate_item(src[:-1], new_lst)
                new_lst.append(src[-1])
            else:
                new_lst.append(src)
        except:
            pass

    split_lst = source.split('\n')
    working_lst = []
    for e in split_lst:
        if '#' in e:
            print('in working lst if')
            e = e[:e.index('#')]
        elif len(e) == 0:
            split_lst.remove(e)
        working_lst += e.split()

    new_split = []
    for i in range(len(working_lst)):
        j = i
        if working_lst[i][0] == '#':
            while j < len(working_lst) and working_lst[j] != '\\n':
                j += 1
            i = j
        else:
            separate_item(working_lst[i], new_split)
    return new_split
    



def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """

    def parse_expression(index):
        try:
            expression = number_or_symbol(tokens[index])
        except:
            pass
        if type(expression) == int or type(expression) == float:
            return expression, index + 1
        elif expression == ')':
            raise CarlaeSyntaxError
        elif expression == '(':
            new_index = index + 1
            if new_index >= len(tokens):
                raise CarlaeSyntaxError
            new_list = []
            try:
                while tokens[new_index] != ')':
                    new_expression, new_index = parse_expression(new_index)
                    new_list.append(new_expression)
                return new_list, new_index + 1 
            except:
                raise CarlaeSyntaxError
        return expression, index + 1
    if tokens.count('(') != tokens.count(')') or len(tokens) > 1 and tokens[0] != '(':
        raise CarlaeSyntaxError
    new_index = 0
    parsed_expression, new_index = parse_expression(new_index)
    return parsed_expression


######################
# Built-in Functions #
######################


carlae_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": lambda args: args[0] if len(args) == 1 else mult(args),
    "/": lambda args: args[0] if len(args) == 1 else div(args)
}

def mult(args):
    result = 1
    for e in args:
        result *= e
    return result

def div(args):
    result = args[0]
    for e in args[1:]:
        result /= e
    return result

############################
# Environments #
############################

class Environment():
    def __init__(self, parent = None, bindings = None):
        self.bindings = bindings
        self.parent = parent
    
    def look_up_var(self, var):
        try:
            print(self.bindings)
            if var in self.bindings:
                return self.bindings[var]
            else:
                return self.parent.look_up_var(var)
        except:
            raise CarlaeNameError
    
    def define_var(self, var, value = None):
        self.bindings[var] = value





##############
# Evaluation #
##############


def evaluate(tree, env = None):
    """
    Evaluate the given syntax tree according to the rules of the Carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    # if no environment is given,
    if env == None:
        print('is none')
        parent = Environment()
        parent.bindings = carlae_builtins
        env = Environment(parent, {})

    if type(tree) == int or type(tree) == float:
        return tree
    elif type(tree) == str:
        # print('looking up 1')
        print(env.bindings)
        return env.look_up_var(tree)
    elif tree[0] == ':=':
        # print('assignemnt is true')
        env.define_var(tree[1], evaluate(tree[2], env))
        # print('defined var')
        return env.look_up_var(tree[1])
    elif type(tree) == list:
        if type(tree[0]) == int or type(tree[0]) == float:
            raise CarlaeEvaluationError
        lam_fnc = evaluate(tree[0], env)
        arguments = [evaluate(args, env) for args in tree[1:]]
        return lam_fnc(arguments)
    else:
        lam_fnc = env.look_up_var(tree[0])
        arguments = [evaluate(args, env) for args in tree[1:]]
        return lam_fnc(arguments)


def REPL():
    while True:
        user_input = input('in> ')
        if user_input != 'EXIT':
            try:
                print('out> ', evaluate(parse(tokenize(user_input))))
            except:
                print('an exception has been raised')
                pass
        else:
            break

def result_and_env(tree, env = None):
    if env == None:
        parent = Environment()
        parent.bindings = carlae_builtins
        env = Environment(parent, {})
    
    return evaluate(tree, env), env



if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    REPL()
