"""6.009 Lab 9: Carlae Interpreter Part 2"""

import sys
from xxlimited import new
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
    "/": lambda args: args[0] if len(args) == 1 else div(args),
    "@t": True,
    "@f": False,
    "=?": lambda args: equal(args),
    "<": lambda args: inc(args),
    ">": lambda args: dec(args),
    "<=": lambda args: noninc(args),
    ">=": lambda args: nondec(args),
    "not": lambda args: notcar(args),
    "pair": lambda args: pair(args),
    "head": lambda args: head(args),
    "tail": lambda args: tail(args),
    "list": lambda args: build_lst(args),
    "list?": lambda args: islist(args),
    "length": lambda args: lenlist(args[0], 0),
    "nth": lambda args: indexlst(args[0], args[1]),
    "concat": lambda args: concat(args),
    "map": None,
    "filter": None,
    "reduce": None
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
def equal(args):
    if len(set(args)) == 1:
        return True
    return False

def inc(args):
    prev = -100000000000
    for e in args:
        if prev >= e:
            return False
        prev = e
    return True

def dec(args):
    prev = 100000000000
    for e in args:
        if prev <= e:
            return False
        prev = e
    return True

def noninc(args):
    prev = -100000000000
    for e in args:
        if prev > e:
            return False
        prev = e
    return True

def nondec(args):
    prev = 100000000000
    for e in args:
        if prev < e:
            return False
        prev = e
    return True

def notcar(args):
    if len(args) == 1:
        return not args[0]
    else:
        raise CarlaeEvaluationError

def pair(args):
    if len(args) == 2:
        return Pair(args[0], args[1])
    else:
        raise CarlaeEvaluationError

def head(args):
    if len(args) != 1 or type(args[0]) != Pair:
        raise CarlaeEvaluationError
    else:
        return args[0].get_head()

def tail(args):
    if len(args) != 1 or type(args[0]) != Pair:
        raise CarlaeEvaluationError
    else:
        return args[0].get_tail()

def build_lst(args):
    if len(args) == 0:
        return None
    else:
        return Pair(args[0], build_lst(args[1:]))

def islist(args):
    if type(args[0]) == Pair and args[0].get_tail() != None:
        return True
    return False

def lenlist(args, count):
    try:
        if args == None:
            return 0
        elif args.get_tail() != None:
            return lenlist(args.get_tail(), count + 1)
        else:
            return count + 1
    except:
        raise CarlaeEvaluationError

def indexlst(args, count):
    try:
        if args == None or count < 0:
            raise CarlaeEvaluationError
        if count == 0:
            return args.get_head()
        elif args.get_tail() != None:
            return indexlst(args.get_tail(), count - 1)
        else:
            raise CarlaeEvaluationError
    except:
        raise CarlaeEvaluationError

def concat(args = None):
    lst = []
    for l in args:
        nxt = l
        while (nxt != None):
            if type(nxt) != Pair:
                raise CarlaeEvaluationError
            head = nxt.get_head()
            lst.append(head)
            nxt = nxt.get_tail()
    return build_lst(lst)



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

class Pair():

    def __init__(self, head, tail):
        """"
        Initializes a pair
        """
        self.head = head
        self.tail = tail

    def get_head(self):
        return self.head

    def get_tail(self):
        return self.tail



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

    if tree == 'nil':
        return None

    if type(tree) == int or type(tree) == float:
        return tree

    #looks up the value associated with a variable
    elif type(tree) == str:
        return env.look_up_var(tree)


    #evaluates an expression recursively, checking the values associated with all vars
    elif type(tree) == list:
        if len(tree) == 0:
            raise CarlaeEvaluationError
        if type(tree[0]) == int or type(tree[0]) == float:
            raise CarlaeEvaluationError

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

        #evaluates conditionals
        elif tree[0] == 'if':
            evalt = evaluate(tree[1], env)
            if evalt:
                return evaluate(tree[2], env)
            else:
                return evaluate(tree[3], env)

        #creates a function object if it detects the function keyword
        elif tree[0] == 'function':
            return Function(env, tree[1], tree[2])

        elif tree[0] == 'and':
            for elem in tree[1:]:
                if evaluate(elem, env) != True:
                    return False
            return True

        elif tree[0] == 'or':
            for elem in tree[1:]:
                if evaluate(elem, env) == True:
                    return True
            return False

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
                # print(tokenize(user_input))
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
    # doctest.testmod())
    # print(parse([]))
    # print(repr(build_lst([3, 4, 5])))
    REPL()
    # print(islist(Pair(1, Pair(2, Pair(3, Pair(4, None))))))
