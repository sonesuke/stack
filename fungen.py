from pyparsing import *
import re


class Environment(object):

    def __init__(self, devkind, offset, module):
        self.devkind = devkind
        self.offset = offset
        self.module = module
        self.functions = []

    def append_function(self, func):
        self.functions.append(func)


name = Word(alphanums)
type_string = Word(alphas)

assign_table = {
    'WORD': {'size': 2, 'assign': '%s = %s'},
    'DWORD': {'size': 2, 'assign': '%s = %s'}
}


def get_size(type_string):
    return assign_table[type_string]['size']


def get_assign_string(type_string, device):
    return assign_table[type_string]['assign'] % (device, '%s')


class Arg(object):

    def __init__(self, name, type_string):
        self.name = name
        self.type_string = type_string
        self.size = get_size(type_string)

    def assign(self, env):
        self.device = env.devkind + str(env.offset)
        self.assign_string = get_assign_string(self.type_string, self.device)


arg = name.setResultsName('Name')
arg += Literal(':')
arg += type_string.setResultsName('Type') + Literal(';')
arg.setParseAction(lambda ts: Arg(ts['Name'], ts['Type']))


class ArgsInput(object):

    def __init__(self, args):
        self.args = args
        self.size = reduce(lambda x, y: x + y, map(lambda x: x.size, args))

    def assign(self, env):
        for a in self.args:
            a.assign(env)
            env.offset += a.size


args_input = CaselessKeyword('var_input')
args_input += Group(OneOrMore(arg)).setResultsName('Args')
args_input += CaselessKeyword('end_var')
args_input.setParseAction(lambda ts: ArgsInput(ts['Args']))


class ArgsLocal(object):

    def __init__(self, args):
        self.args = args
        self.size = sum([a.size for a in self.args])

    def assign(self, env):
        for a in self.args:
            a.assign(env)
            env.offset += a.size


args_local = CaselessKeyword('var')
args_local += Group(OneOrMore(arg)).setResultsName('Args')
args_local += CaselessKeyword('end_var')
args_local.setParseAction(lambda ts: ArgsLocal(ts['Args']))


class Statement(object):

    def __init__(self, st):
        self.statement = st

end_function = CaselessKeyword('end_function')
statement = NotAny(end_function) + Regex(".*").setResultsName('Statement')
statement.setParseAction(lambda ts: Statement(ts['Statement']))


def substitute(target, arg):
    return re.sub(target, arg.name, arg.device)


class Funcall(object):

    def __init__(self, name, args):
        self.name = name
        self.args = [p.strip() for p in args.split(',') if len(p.strip()) != 0]

    def assign_args(self, f):
        ret = ""
        if f.args_input is None:
            return ret
        assert len(f.args_input.args) == len(self.args)
        for i in range(len(self.args)):
            l = f.args_input.args[i].assign_string % self.args[i]
            ret += l + "\n"
        return ret

    def alocate(self, f):
        for i in range(len(self.args)):
            if f.args_input is not None and f.args_input.size > 0:
                for a in f.args_input.args:
                    self.args[i] = substitute(self.args[i], a)
            if f.args_local is not None and f.args_local.size > 0:
                for a in f.args_local.args:
                    self.args[i] = substitute(self.args[i], a)

    def assign(self, env):
        self.converted = ""
        for f in env.functions:
            if f.name == self.name:
                self.converted = self.assign_args(f)
                self.converted += 'ECall("%s", %s)' % (env.module, self.name)


funcall = Literal('funcall') + name.setResultsName('Name')
funcall += Literal('(')
funcall += Regex(r'[^)]*').setResultsName('Args')
funcall += Literal(')')
funcall.setParseAction(lambda ts: Funcall(ts['Name'], ts['Args']))
body = Group(ZeroOrMore(funcall | statement)).setResultsName('Body')
body.setParseAction(lambda ts: ts['Body'])


class Function(object):

    def __init__(self, name, type_string, args_input, args_local, body):
        self.name = name
        self.ret_type = type_string
        self.args_local = None
        self.args_input = None
        self.size = 0
        if len(args_input) > 0:
            self.args_input = args_input[0]
            self.size += self.args_input.size
        self.args_local = None
        if len(args_local) > 0:
            self.args_local = args_local[0]
            self.size += self.args_local.size
        self.body = body

    def assign(self, env):
        if self.args_input is not None:
            self.args_input.assign(env)
        if self.args_local is not None:
            self.args_local.assign(env)

    def alocate(self):
        for b in self.body:
            b.alocate(self)


function = CaselessKeyword('function')
function += name.setResultsName('Name')
function += Literal(':')
function += type_string.setResultsName('Type')
function += Group(Optional(args_input)).setResultsName('Input')
function += Group(Optional(args_local)).setResultsName('Local')
function += body.setResultsName('Body')
function += end_function
function.setParseAction(
    lambda ts: Function(
        ts['Name'],
        ts['Type'],
        ts['Input'],
        ts['Local'],
        ts['Body']))
