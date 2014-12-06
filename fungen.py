from pyparsing import *


name = Word(alphanums)
type_string = Word(alphas)


class Arg(object):

    def __init__(self, name, type_string):
        self.name = name
        self.type_string = type_string

arg = name.setResultsName('Name')
arg += Literal(':')
arg += type_string.setResultsName('Type') + Literal(';')
arg.setParseAction(lambda ts: Arg(ts['Name'], ts['Type']))


class ArgsInput(object):

    def __init__(self, args):
        self.args = args

args_input = CaselessKeyword('var_input')
args_input += Group(OneOrMore(arg)).setResultsName('Args')
args_input += CaselessKeyword('end_var')
args_input.setParseAction(lambda ts: ArgsInput(ts['Args']))


class ArgsLocal(object):

    def __init__(self, args):
        self.args = args

args_local = CaselessKeyword('var')
args_local += Group(OneOrMore(arg)).setResultsName('Args')
args_local += CaselessKeyword('end_var')
args_local.setParseAction(lambda ts: ArgsLocal(ts['Args']))


class Function(object):

    def __init__(self, name, type_string, local):
        self.name = name
        self.ret_type = type_string
        self.args_local = local

function = CaselessKeyword('function')
function += name.setResultsName('Name')
function += Literal(':').setResultsName('Local')
function += type_string.setResultsName('Type')
function += Optional(args_local)
function += CaselessKeyword('end_function')
function.setParseAction(
    lambda ts: Function(ts['Name'], ts['Type'], ts['Local']))


class Parser(object):

    def __init__(self):
        pass

    def function(self, text):
        return function.parseString(text)[0]

    def args_local(self, text):
        return args_local.parseString(text)[0]

    def args_input(self, text):
        return args_input.parseString(text)[0]

    def arg(self, text):
        return arg.parseString(text)[0]
