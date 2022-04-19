"""6.009 Lab 9: Carlae Interpreter Part 2"""

import sys
sys.setrecursionlimit(10_000)

# KEEP THE ABOVE LINES INTACT, BUT REPLACE THIS COMMENT WITH YOUR lab.py FROM
# THE PREVIOUS LAB, WHICH SHOULD BE THE STARTING POINT FOR THIS LAB.
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
        """
        Separates values inside a pair of parenthesis
        """
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

    #splits source based on line splits
    split_lst = source.split('\n')
    working_lst = []
    for e in split_lst:
        #ignores comments 
        if '#' in e:
            print('in working lst if')
            e = e[:e.index('#')]
        elif len(e) == 0:
            split_lst.remove(e)
        working_lst += e.split()

    new_split = []
    #splits source based on white spaces
    for i in range(len(working_lst)):
        #separates items
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
        #returns expression if it is an int or float
        if type(expression) == int or type(expression) == float:
            return expression, index + 1

        #expression cannot start with )
        elif expression == ')':
            raise CarlaeSyntaxError

        #recursively checks the inside of parenthesis
        elif expression == '(':
            new_index = index + 1
            if new_index >= len(tokens):
                raise CarlaeSyntaxError
            new_list = []
            try:
                #keeps checking inside expression until a closed parenthesis is met
                while tokens[new_index] != ')':
                    new_expression, new_index = parse_expression(new_index)
                    new_list.append(new_expression)
                return new_list, new_index + 1 
            except:
                #the parenthesis is never closed
                raise CarlaeSyntaxError
        return expression, index + 1

    # checks that all parenthesis are matched
    if tokens.count('(') != tokens.count(')') or len(tokens) > 1 and tokens[0] != '(':
        raise CarlaeSyntaxError
    new_index = 0
    parsed_expression, new_index = parse_expression(new_index)
    return parsed_expression


#################################
# Built-in Functions and Helpers#
################################


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

###########
# Classes #
###########

class Environment():
    def __init__(self, parent = None, bindings = None):
        """"
        Initializes a new Environment
        """
        self.bindings = bindings
        self.parent = parent
    
    def look_up_var(self, var):
        """
        Looks up the value associated with a variable in its environment and parent environments
        or returns exception if it is not found
        """
        try:
            if var in self.bindings:
                return self.bindings[var]
            else:
                return self.parent.look_up_var(var)
        except:
            #var has not been assigned
            raise CarlaeNameError
    
    def define_var(self, var, value = None):
        """
        Assignns a value to a variable
        """
        self.bindings[var] = value

class Function():
    def __init__(self, env = None, parameters = None, expression= None):
        """"
        Initializes a user created function
        """
        self.env = env
        self.params = parameters
        self.expression = expression

    def __call__(self, args):
        """"
        Calls a user created function
        """
        temp = {}
        if len(self.params) != len(args):
            raise CarlaeEvaluationError

        #creates a dictionary of new assignments for the new environment tied to func
        for i in range(len(args)):
            temp[self.params[i]] = args[i]
        return evaluate(self.expression, Environment(self.env, temp))






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
    # if no environment is given, create one
    if env == None:
        env = Environment(Environment(None, carlae_builtins), {})

    if type(tree) == int or type(tree) == float:
        return tree

    #looks up the value associated with a variable
    elif type(tree) == str:
        return env.look_up_var(tree)

    #assigns a value to a variable (could assign function or expression)
    elif tree[0] == ':=':
        name = tree[1]
        #assigning function
        if type(tree[1]) == list:
            name = tree[1][0]
            args = tree[1][1:]
            new_value = evaluate(['function', args, tree[2]], env)
        #assigning expression
        else:
            new_value = evaluate(tree[2], env)
        env.define_var(name, new_value)
        return new_value

    #creates a function object if it detects the function keyword
    elif tree[0] == 'function':
        return Function(env, tree[1], tree[2])

    #evaluates an expression recursively, checking the values associated with all vars
    elif type(tree) == list:
        if type(tree[0]) == int or type(tree[0]) == float:
            raise CarlaeEvaluationError
        lam_fnc = evaluate(tree[0], env)
        arguments = [evaluate(args, env) for args in tree[1:]]
        return lam_fnc(arguments)

    #evaluates a simple expression
    else:
        lam_fnc = env.look_up_var(tree[0])
        arguments = [evaluate(args, env) for args in tree[1:]]
        return lam_fnc(arguments)


def REPL(env = None):
    while True:
        #keeps taking inputs until EXIT
        if env == None:
            env = Environment(Environment(None, carlae_builtins), {})
        user_input = input('in> ')
        if user_input != 'EXIT':
            try:
                print('out> ', evaluate(parse(tokenize(user_input)), env))
            except:
                print('an exception has been raised')
                pass
        else:
            break

def result_and_env(tree, env = None):
    # if no environment is given, create one
    if env == None:
        env = Environment(Environment(None, carlae_builtins), {})

    return evaluate(tree, env), env



if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    REPL()
