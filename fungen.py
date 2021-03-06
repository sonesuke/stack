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
type_string = Regex(r'[*a-zA-Z]+')

assign_table = {
    'WORD': {'size': 2, 'assign': '%s = %s'},
    '*WORD': {'size': 2, 'assign': 'ADRSET(%s, %s)'},
    'DWORD': {'size': 2, 'assign': '%s = %s'},
    '*DWORD': {'size': 2, 'assign': 'ADRSET(%s, %s)'},
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

    def compile(self, context_f, env):
        f = context_f
        if f.args_input is not None and f.args_input.size > 0:
            for a in f.args_input.args:
                self.statement = substitute(self.statement, a)
        if f.args_local is not None and f.args_local.size > 0:
            for a in f.args_local.args:
                self.statement = substitute(self.statement, a)
        self.converted = self.statement

end_function = CaselessKeyword('end_function')
statement = NotAny(end_function) + Regex(".*").setResultsName('Statement')
statement.setParseAction(lambda ts: Statement(ts['Statement']))


def substitute(target, arg):
    return re.sub(arg.name, arg.device, target)


class Funcall(object):

    def __init__(self, name, args):
        self.name = name
        self.args = [p.strip() for p in args.split(',') if len(p.strip()) != 0]

    def compile_args(self, f):
        ret = ""
        if f.args_input is None:
            return ret
        assert len(f.args_input.args) == len(self.args)
        for i in range(len(self.args)):
            l = f.args_input.args[i].assign_string % self.args[i]
            ret += l + "\n"
        return ret

    def compile(self, context_f, env):
        f = context_f
        for i in range(len(self.args)):
            if f.args_input is not None and f.args_input.size > 0:
                for a in f.args_input.args:
                    self.args[i] = substitute(self.args[i], a)
            if f.args_local is not None and f.args_local.size > 0:
                for a in f.args_local.args:
                    self.args[i] = substitute(self.args[i], a)
        for fs in env.functions:
            if fs.name == self.name:
                f = fs
        self.converted = ""
        self.converted = self.compile_args(f)
        self.converted += 'ECall("%s", %s)' % (env.module, self.name)


funcall = Literal('funcall') + name.setResultsName('Name')
funcall += Literal('(')
funcall += Regex(r'[^)]*').setResultsName('Args')
funcall += Literal(')')
funcall.setParseAction(lambda ts: Funcall(ts['Name'], ts['Args']))
body = Group(ZeroOrMore(funcall | statement)).setResultsName('Body')
body.setParseAction(lambda ts: ts['Body'])


indent_table = {
    'FOR': {'before': 0, 'after': 1},
    'NEXT': {'before': -1, 'after': 0},
    'IF': {'before': 0, 'after': 1},
    'ELSE': {'before': 0, 'after': 1},
    'SELECT': {'before': 0, 'after': 1},
    'END': {'before': -1, 'after': 0},
}


def before_indent(txt):
    import re
    for t in indent_table.keys():
        if re.match(r'^\s*' + t, txt) is not None:
            return indent_table[t]['before']
    return 0

def after_indent(txt):
    import re
    for t in indent_table.keys():
        if re.match(r'^\s*' + t, txt) is not None:
            return indent_table[t]['after']
    return 0


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

    def compile(self, env):
        for b in self.body:
            b.compile(self, env)
        self.converted = ""
        self.converted += '!!SBN %s\n' % self.name
        for b in self.body:
            self.converted += b.converted + '\n'
        self.converted += '!!RET\n'

    def pretty(self):
        lines = self.converted.split('\n')
        indent = 0
        self.converted = ""
        for l in lines:
            indent += before_indent(l)
            self.converted += ' ' * 4 * indent
            self.converted += l + '\n'
            indent += after_indent(l)


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


class Program(object):

    def __init__(self, funs):
        self.funs = funs

    def compile(self, env):
        for f in self.funs:
            f.assign(env)
            env.append_function(f)
        self.converted = ""
        for f in self.funs:
            f.compile(env)
            f.pretty()
            self.converted += f.converted


program = ZeroOrMore(function).setResultsName('Functions')
program.setParseAction(lambda ts: Program(ts['Functions']))


if __name__ == '__main__':
    import sys
    import re

    argvs = sys.argv
    argc = len(argvs)
    if (argc != 4):
        print 'Usage: #python %s filename device module' % argvs[0]
        quit()
    filename = argvs[1]
    device = argvs[2]
    module = argvs[3]
    m = re.search(r'([a-zA-Z]+)([0-9]+)', device)
    dvkind = m.group(1)
    offset = int(m.group(2))

    a = program.parseFile(filename)[0]
    env = Environment(dvkind, offset, module)
    a.compile(env)
    print a.converted
