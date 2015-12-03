""" lisp interpreter in python """

Symbol = str   #Scheme Symbol as Python str
List = list    #Scheme List as Python list
Number = (int, float)    #Scheme Number as Python int or float
#nv = dict    #it is a mapping of {variable: value}

######## Parsing

def parse(program):
    "read Scheme expression from a string"
    return read_from_tokens(tokenize(program))

def tokenize(string):
    " Convert the string into a list of tokens"
    return string.replace('(', ' ( ').replace(')', ' ) ').split()

def read_from_tokens(tokens):
    "Read an expression from seqof tokens"
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token :
        lst = []
        while tokens[0] != ')':
            lst.append(read_from_tokens(tokens))
        tokens.pop(0)   # pop off ')'
        return lst
    elif ')' == token :
        raise SyntaxError ('unexpected )')
    else :
        return atom(token)

def atom(token) :
    "Numbers becom numbers every other token is a symbol"
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)

######## Environments

def standard_env() :
    "An environment with some Scheme standard procedures."
    import math, operator as op
    env = Env()
    env.update(vars(math)) # sin, cos, sqrt, pi,....
    env.update({
        '+' : op.add, '-' : op.sub, '*' : op.mul, '/' : op.div,
        '>' : op.gt, '<' :op.lt, '>=' : op.ge, '<=' : op.le,
        '=' : op.eq, 'abs' : abs, 'append' : op.add,
        'apply' : apply, 'begin' : lambda *x: x[-1],
        'car' : lambda x : x[0], 'cdr' : lambda x: x[1:],
        'cons' : lambda x,y: [x] + y,
        'eq?' : op.is_, 'equal?' : op.eq,
        'length' : len, 'list' : lambda *x: list(x),
        'list?' : lambda x:isinstance(x, list),
        'map' : map, 'max' : max, 'min' : min,
        'not' : op.not_, 'null?' : lambda x: x== [],
        'number?' : lambda x: isinstance(x, Number),
        'procedure?' : callable, 'round' : round,
        'symbol?' : lambda x: isinstance(x, Symbol),
    })
    return env

class Env(dict):
    
    "An environment : a dict of {'var': value} pairs"
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer

    def find(self, var):
        "find innermost environment where 'var' appears."
        return self if (var in self) else self.outer.find(var)

global_env = standard_env()

###### Interaction

def repl(prompt = 'lis.py>'):
    " A prompt -read-value-print-loop."
    while True:
        val = eval1(parse(raw_input(prompt)))
        if val is not None :
            print(Schemestr(val))

def Schemestr(exp):
    " Convert a python object into a Scheme readable string"
    if isinstance(exp, list) :
        return '(' + ' '.join(map(Schemestr, exp)) + ')'
    else :
        return str(exp)


#### Procedure

class Procedure:

    "A user defined scheme procedure"
    def __init__(self, parms, body, env):
        self.parms = parms
        self.body = body
        self.env = env

    def __call__(self, *args):
        return eval1(self.body, Env(self.parms, args, self.env))

##### eval

def eval1(x, env = global_env) :
    " Evaluate an expression in an Environment"
    if isinstance(x, Symbol) :    # variable reference
#        env[x]
#        print env.find(x)[x]
        return env.find(x)[x]
#        print env[x]
    elif not isinstance(x, List) :  # constant literal
        return x
    elif x[0] == 'quote' :    # quote exp
        (_, exp) = x
#        print exp
        return exp
    elif x[0] == 'if' :    # if test conseq alt
        (_, test, conseq, alt) = x
        exp = (conseq if eval1(test, env) else alt)
#        print eval(exp, env)
        return eval1(exp, env)
    elif x[0] == 'define' :    # define var exp
        (_, var, exp) = x
        env[var] = eval1(exp, env)
#        print env[var]
    elif x[0] == 'set!' :
        (_, var, exp) = x
        env.find(var)[var] = eval1(exp, env)
    elif x[0] == 'lambda' :
        (_, parms, body) = x
        return Procedure(parms, body, env)
    else :
        proc = eval1(x[0], env)    # procedure
#        print x[0]
#        print proc
        args = [eval1(arg, env) for arg in x[1:]]
#        print args
        return proc(*args)

###### REPL


program = "(define r 10)"
program2 = "(* pi (* r r))" 
#print standard_env()
#print parse(program2)
print eval1(parse(program))
print eval1(parse(program2))
#repl()
