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


class Var(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n
        self.rank = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Var(" + repr(self.name) + ")"

    def deriv(self, value):
        if self.name == value:
            return Num(1)
        else:
            return Num(0)

    def simplify(self):
        return self

    def eval(self, mapping):
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
        self.rank = None

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return "Num(" + repr(self.n) + ")"

    def deriv(self, value):
        return Num(0)

    def simplify(self):
        return self

    def eval(self, mapping):
        return self.n


class BinOp(Symbol):
    def __init__(self, left, right):
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


class Add(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.rank = 0

    def __str__(self):
        return str(self.left) + " + " + str(self.right)

    def __repr__(self):   
        return "Add(" + repr(self.left) + "," + repr(self.right) + ")"

    def deriv(self, value):
        return self.left.deriv(value) + self.right.deriv(value)

    def simplify(self):
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
        return self.left.eval(mapping) + self.right.eval(mapping)

class Sub(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.rank = 1

    def __str__(self):
        if self.right.rank is not None and self.right.rank < 2:
            return str(self.left) + " - (" + str(self.right) + ")"
        return str(self.left) + " - " + str(self.right)

    def __repr__(self):
        return "Sub(" + repr(self.left) + "," + repr(self.right) + ")"

    def deriv(self, value):
        return self.left.deriv(value) - self.right.deriv(value)

    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        if type(self.right) == Num and self.right.n == 0:
            return self.left
        elif type(self.right)==Num and type(self.left)==Num:
            return Num(self.left.n - self.right.n)
        else:
            return self.left - self.right

    def eval(self, mapping):
        return self.left.eval(mapping) - self.right.eval(mapping)

class Mul(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.rank = 2

    def __str__(self):
        if self.right.rank is not None and self.left.rank is not None and self.left.rank < 2 and self.right.rank < 2:
            return "(" + str(self.left) + ") * (" + str(self.right) + ")"
        elif self.left.rank is not None and  self.left.rank < 2:
            return "(" + str(self.left) + ") * " + str(self.right)
        elif self.right.rank is not None and self.right.rank < 2:
            return str(self.left) + " * (" + str(self.right) + ")"
        return str(self.left) + " * " + str(self.right)

    def __repr__(self):
        return "Mul(" + repr(self.left) + "," + repr(self.right) + ")" 

    def deriv(self, value):
        return (self.left.deriv(value) * self.right) + (self.right.deriv(value) * self.left)

    def simplify(self):
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
        return self.left.eval(mapping) * self.right.eval(mapping)

            

class Div(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.rank = 3

    def __str__(self):
        if self.right.rank is not None and self.right.rank < 2 and self.left.rank is not None and self.left.rank < 2:
            return "(" + str(self.left) + ") / (" + str(self.right) + ")"
        elif self.right.rank is not None and self.right.rank < 4:
            if self.left.rank is not None and self.left.rank < 2:
                return  "(" + str(self.left) + ") / (" + str(self.right) + ")"
            return str(self.left) + " / (" + str(self.right) + ")"
        elif self.left.rank is not None and self.left.rank < 2:
            return "(" + str(self.left) + ") / " + str(self.right)
        return str(self.left) + " / " + str(self.right)

    def __repr__(self):
        return "Div(" + repr(self.left) + "," + repr(self.right) + ")" 

    def deriv(self, value):
        return ((self.left.deriv(value)*self.right) - (self.right.deriv(value)*self.left)) / ((self.right)* (self.right))

    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        if type(self.left) == Num and self.left.n ==0:
            return Num(0)
        elif type(self.right) == Num and int(self.right.n) == 1:
            return self.left
        elif type(self.left) == Num and type(self.right) == Num:
            return Num(self.left.n/self.right.n)
        else:
            return self.left/ self.right

    def eval(self, mapping):
        return self.left.eval(mapping) / self.right.eval(mapping)



if __name__ == "__main__":
    # doctest.testmod()
    print(Add(Num(0), Var('x')).simplify())
    # ("Add(Num(0), Mul(Var('y'), Num(2)))", '0 + y * 2')
