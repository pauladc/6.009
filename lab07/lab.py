import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:

    def __add__(self, right):
        return Add(self, right)
    def __radd__(self, right):
        return Add(right, self)
    def __sub__(self, right):
        return Sub(self, right)
    def __rsub__(self, right):
        return Sub(right, self)
    def __mul__(self, right):
        return Mul(self, right)
    def __rmul__(self, right):
        return Mul(right, self)
    def __truediv__(self, right):
        return Div(self, right)
    def __rtruediv__(self, right):
        return Div(right, self)
    def __pow__(self, right):
        return Pow(self, right)
    def __rpow__(self, right):
        return Pow(right, self)


class Var(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n
        self.rank = 0

    def __str__(self):
        """
        Produces a human readable form of the expression
        """
        return self.name

    def __repr__(self):
        """
        Represents a number in its equivalent form
        """
        return "Var(" + repr(self.name) + ")"

    def deriv(self, value):
        """
        Returns the derivative of a variable
        """
        if self.name == value:
            return Num(1)
        else:
            return Num(0)

    def simplify(self):
        """
        Simplifies the expression
        """
        return self

    def eval(self, mapping):
        """
        Evaluates the expression 
        """
        try:
            return mapping[self.name]
        except:
            return 1




class Num(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n
        self.rank = 0

    def __str__(self):
        """
        Produces a human readable form of the expression
        """
        return str(self.n)

    def __repr__(self):
        """
        Represents a number in its equivalent form
        """
        return "Num(" + repr(self.n) + ")"

    def deriv(self, value):
        """
        Returns the derivative of a number
        """
        return Num(0)

    def simplify(self):
        """
        Simplifies the expression
        """
        return self

    def eval(self, mapping):
        """
        Evaluates the expression 
        """
        return self.n


class BinOp(Symbol):
    def __init__(self, left, right):
        '''
        Initializes operator class. Identifies items as variables or numbers 
        and produces str and repr representations.
        '''
        if isinstance(right, Symbol):
            self.right = right
        else:
            if type(right) == int or type(right) == float:
                self.right = Num(right)
            else:
                self.right = Var(right)
        if isinstance(left, Symbol):
            self.left = left
        else:
            if type(left) == int or type(left) == float:
                self.left = Num(left)
            else:
                self.left = Var(left)
    def __repr__(self):
        """
        Represents all operations as equivalent forms
        """
        op_symb = {' + ': 'Add', ' - ': 'Sub', ' * ': 'Mul', ' / ': 'Div', ' ** ': 'Pow'}
        placeholder = '({}, {})'
        return op_symb[self.operation] + placeholder.format(repr(self.left), repr(self.right))

    def __str__(self):
        """
        Produces human readable representations
        """
        l, r = str(self.left), str(self.right)
        if self.left.rank != 0 and self.rank == 3:
            l = '(' + l + ')'
        elif self.left.rank != 0 and self.left.rank < self.rank:
            l  = '(' + l + ')'
        if self.right.rank != 0 and self.right.rank < self.rank:
            r  = '(' + r + ')'
        elif self.special and self.right.rank != 0 and self.rank == self.right.rank:
            r  = '(' + r + ')'
        return '{}{}{}'.format(l, self.operation, r)




class Add(BinOp):
    def __init__(self, left, right):
        """
        Initializer for addition.  Store an instance variables rank, operation and special, used
        to determine the precedence order and the symbol associated with each operation.
        """
        super().__init__(left, right)
        self.rank = 1
        self.operation = ' + '
        self.special = False

    def deriv(self, value):
        """
        Finds the derivative of an addition
        """
        return self.left.deriv(value) + self.right.deriv(value)

    def simplify(self):
        """
        Simplifies addition, accounting for zeros
        """
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        print(type(self.left), type(self.right))
        if type(self.left)== Num and self.left.n == 0:
            return self.right
        elif type(self.right) == Num and self.right.n == 0:
            return self.left
        elif type(self.right) == Num and type(self.left) == Num:
            return Num(self.right.n + self.left.n)
        else:
            return self.left + self.right

    def eval(self, mapping):
        """
        Evaluates the expression
        """
        return self.left.eval(mapping) + self.right.eval(mapping)

class Sub(BinOp):
    def __init__(self, left, right):
        """
        Initializer for substriction.  Store an instance variables rank, operation and special, used
        to determine the precedence order and the symbol associated with each operation.
        """
        super().__init__(left, right)
        self.rank = 1
        self.operation = ' - '
        self.special = True

    def deriv(self, value):
        """
        Finds the derivative of a substraction
        """
        return self.left.deriv(value) - self.right.deriv(value)

    def simplify(self):
        """
        Simplifies subtraction, accounting for zeros
        """
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        if type(self.right) == Num and self.right.n == 0:
            return self.left
        elif type(self.right)==Num and type(self.left)==Num:
            return Num(self.left.n - self.right.n)
        else:
            return self.left - self.right

    def eval(self, mapping):
        """
        Evaluates the expression
        """
        return self.left.eval(mapping) - self.right.eval(mapping)

class Mul(BinOp):

    def __init__(self, left, right):
        """
        Initializer for substriction.  Store an instance variables rank, operation and special, used
        to determine the precedence order and the symbol associated with each operation.
        """
        super().__init__(left, right)
        self.rank = 2
        self.operation = ' * '
        self.special = False

    def deriv(self, value):
        """
        Finds the derivative of a multiplication using the product rule
        """
        return (self.left.deriv(value) * self.right) + (self.right.deriv(value) * self.left)

    def simplify(self):
        """
        Simplifies multiplication, considering cases where the expression is multiplied by one or zero
        """
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        if type(self.left) == Num and self.left.n == 0 or type(self.right) == Num and self.right.n == 0:
            return Num(0)
        elif type(self.right) == Num and int(self.right.n) == 1:
            return self.left
        elif type(self.left) == Num and int(self.left.n) == 1:
            return self.right
        elif type(self.left) == Num and type(self.right) == Num:
            return Num(self.left.n*self.right.n)
        else:
            return self.right * self.left

    def eval(self, mapping):
        """
        Evaluates the expression
        """
        return self.left.eval(mapping) * self.right.eval(mapping)

            

class Div(BinOp):
    def __init__(self, left, right):
        """
        Initializer for division.  Store an instance variables rank, operation and special, used
        to determine the precedence order and the symbol associated with each operation.
        """
        super().__init__(left, right)
        self.rank = 2
        self.operation = ' / '
        self.special = True

    def deriv(self, value):
        """
        Finds the derivative of a division using the quotient rule
        """
        return ((self.left.deriv(value)*self.right) - (self.right.deriv(value)*self.left)) / ((self.right)* (self.right))

    def simplify(self):
        """
        Simplifies division, but it does not account for division by zero
        """
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        if type(self.left) == Num and self.left.n == 0:
            return Num(0)
        elif type(self.right) == Num and int(self.right.n) == 1:
            return self.left
        elif type(self.left) == Num and type(self.right) == Num:
            return Num(self.left.n/self.right.n)
        else:
            return self.left/ self.right

    def eval(self, mapping):
        """
        Evaluates the expression
        """
        return self.left.eval(mapping) / self.right.eval(mapping)

class Pow(BinOp):
    def __init__(self, left, right):
        """
        Initializer for division.  Store an instance variables rank, operation and special, used
        to determine the precedence order and the symbol associated with each operation.
        """
        super().__init__(left, right)
        self.rank = 3
        self.operation = ' ** '
        self.special = False

    def deriv(self, value):
        """
        Finds the derivative of an exponent
        """
        if isinstance(self.right, Num):
            return self.right * (self.left ** (self.right - 1)) * self.left.deriv(value)      
        else:
            raise TypeError('right value is not a number')
    
    def simplify(self):
        """
        Simplifies exponentiation
        """
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        if type(self.right) == Num and self.right.n == 0:
            return Num(1)
        elif type(self.right) == Num and self.right.n == 1:
            return self.left
        elif type(self.left) == Num and self.left.n == 0:
            return Num(0)
        else:
            return self.left ** self.right
    def eval(self, mapping):
        """
        Evaluates the expression
        """
        return self.left.eval(mapping) ** self.right.eval(mapping)






def expression(formula):
    """
    Parses an expression to produce a version interpretable by the program from human readable version
    """
    return parse(tokenize(formula))

def tokenize(formula):
    """ 
    Creates a list that can be interpreted by the parser
    """
    meaning = []
    digits = ''
    for i in range(len(formula)):
        if formula[i].isdigit():
            digits += formula[i]
        elif formula[i] == '-' and formula[i+1].isdigit():
            digits += formula[i]
        elif formula[i] == '*' and formula[i-1] == '*':
            meaning.pop()
            meaning.append('**')
        elif formula[i].isspace():
            if digits != '':
                meaning.append(digits)
                digits = ''
        else:
            if digits != '':
                meaning.append(digits)
                digits = ''
            meaning.append(formula[i])
    if digits != '':
        meaning.append(digits)
    return meaning

def parse(tokens):
    """
    Parses the expression to determine the classes that are appropriate considering the expression
    """
    def parse_expression(index):
        operators = {"+":Add, "-":Sub, "*":Mul, "/":Div, "**":Pow}
        if tokens[index].isalpha():
            return (Var(tokens[index]), index + 1)
        elif tokens[index] == "(":
            left, left_index = parse_expression(index+1)
            operation = operators[tokens[left_index]] 
            right, right_index = parse_expression(left_index+1)
            return (operation(left, right), right_index+1)
        else:
            return (Num(int(tokens[index])), index + 1)

    next_index = 0
    parsed_expression, next_index = parse_expression(next_index)
    return parsed_expression



if __name__ == "__main__":
    # doctest.testmod()
    # print(Add(Num(0), Var('x')).simplify())
    # ("Add(Num(0), Mul(Var('y'), Num(2)))", '0 + y * 2')
    print(tokenize('2**4'))
