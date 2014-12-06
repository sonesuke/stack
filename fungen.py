from pyparsing import *


name = Word(alphanums)
type_string = Word(alphas)

class Arg(object):
    def __init__(self, name, type_string):
        self.name = name
        self.type_string = type_string

arg = name.setResultsName('Name') + Literal(':') + type_string.setResultsName('Type') + Literal(';')
arg.setParseAction(lambda ts: Arg(ts['Name'], ts['Type']))

class ArgsInput(object):
    def __init__(self, args):
        self.args = args

args_input = CaselessKeyword('var_input') + Group(OneOrMore(arg)).setResultsName('Args') + CaselessKeyword('end_var')
args_input.setParseAction(lambda ts: ArgsInput(ts['Args']))


class ArgsLocal(object):
    def __init__(self, args):
        self.args = args

args_local = CaselessKeyword('var') + Group(OneOrMore(arg)).setResultsName('Args') + CaselessKeyword('end_var')
args_local.setParseAction(lambda ts: ArgsLocal(ts['Args']))


class Function(object):
    def __init__(self, name, type_string):
        self.name = name
        self.ret_type = type_string

function = CaselessKeyword('function') + name.setResultsName('Name') + Literal(':') + type_string.setResultsName('Type')
function += CaselessKeyword('end_function')
function.setParseAction(lambda ts: Function(ts['Name'], ts['Type']))

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
