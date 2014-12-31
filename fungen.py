from pyparsing import *


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

    def assign(self, devkind, offset):
        self.device = devkind + str(offset)
        self.assign_string = get_assign_string(self.type_string, self.device)


arg = name.setResultsName('Name')
arg += Literal(':')
arg += type_string.setResultsName('Type') + Literal(';')
arg.setParseAction(lambda ts: Arg(ts['Name'], ts['Type']))


class ArgsInput(object):

    def __init__(self, args):
        self.args = args
        self.size = reduce(lambda x, y: x+y, map(lambda x: x.size, args))

    def assign(self, devkind, offset):
        for a in self.args:
            a.assign(devkind, offset)
            offset += a.size
        return offset


args_input = CaselessKeyword('var_input')
args_input += Group(OneOrMore(arg)).setResultsName('Args')
args_input += CaselessKeyword('end_var')
args_input.setParseAction(lambda ts: ArgsInput(ts['Args']))


class ArgsLocal(object):

    def __init__(self, args):
        self.args = args
        self.size = sum([a.size for a in self.args])

    def assign(self, devkind, offset):
        for a in self.args:
            a.assign(devkind, offset)
            offset += a.size
        return offset


args_local = CaselessKeyword('var')
args_local += Group(OneOrMore(arg)).setResultsName('Args')
args_local += CaselessKeyword('end_var')
args_local.setParseAction(lambda ts: ArgsLocal(ts['Args']))


class Funcall(object):

    def __init__(self, name, args):
        self.name = name
        self.args = [p.strip() for p in args.split(',')]


end_function = CaselessKeyword('end_function')
statement = NotAny(end_function) + Regex(".*").setResultsName('Statement')
statement.setParseAction(lambda ts: ts['Statement'])
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

    def assign(self, devkind, offset):
        if self.args_input is not None:
            offset = self.args_input.assign(devkind, offset)
        if self.args_local is not None:
            offset = self.args_local.assign(devkind, offset)


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
