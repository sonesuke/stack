from fungen import *

import pep8
import glob


def test_pep8():
    pep8style = pep8.StyleGuide()
    result = pep8style.check_files(glob.glob('*.py'))
    assert result.total_errors == 0


def test_arg():
    target = "a1: WORD;"
    a = arg.parseString(target)[0]
    assert isinstance(a, Arg)
    assert a.name == 'a1'
    assert a.type_string == 'WORD'
    assert a.size == 2
    env = Environment('TM', 0, 'Main')
    a.assign(env)
    assert a.device == 'TM0'
    assert a.assign_string == 'TM0 = %s'


def test_input_args():
    target = """
      var_input
          a0: WORD;
          a1: DWORD;
      end_var
      """
    a = args_input.parseString(target)[0]
    assert isinstance(a, ArgsInput)
    assert a.args[0].name == 'a0'
    assert a.args[0].type_string == 'WORD'
    assert a.args[1].name == 'a1'
    assert a.args[1].type_string == 'DWORD'
    env = Environment('TM', 0, 'Main')
    a.assign(env)
    assert a.args[0].device == 'TM0'
    assert a.args[0].assign_string == 'TM0 = %s'
    assert a.args[1].device == 'TM2'
    assert a.args[1].assign_string == 'TM2 = %s'


def test_local_args():
    target = """
      var
          a0: WORD;
          a1: DWORD;
      end_var
      """
    a = args_local.parseString(target)[0]
    assert isinstance(a, ArgsLocal)
    assert a.args[0].name == 'a0'
    assert a.args[0].type_string == 'WORD'
    assert a.args[1].name == 'a1'
    assert a.args[1].type_string == 'DWORD'
    env = Environment('TM', 0, 'Main')
    a.assign(env)
    assert a.args[0].device == 'TM0'
    assert a.args[0].assign_string == 'TM0 = %s'
    assert a.args[1].device == 'TM2'
    assert a.args[1].assign_string == 'TM2 = %s'


def test_function():
    target = """
      function A: void
      end_function
      """
    a = function.parseString(target)[0]
    assert isinstance(a, Function)
    assert a.name == 'A'
    assert a.ret_type == 'void'
    assert a.size == 0


def test_function_with_local():
    target = """
      function A: void
      var
          a0: WORD;
          a1: DWORD;
      end_var
      end_function
      """
    a = function.parseString(target)[0]
    assert isinstance(a, Function)
    assert a.name == 'A'
    assert a.ret_type == 'void'
    assert a.args_local.args[0].name == 'a0'
    assert a.args_local.args[0].type_string == 'WORD'
    assert a.args_local.args[1].name == 'a1'
    assert a.args_local.args[1].type_string == 'DWORD'
    assert a.size == 4
    env = Environment('TM', 0, 'Main')
    a.assign(env)
    assert a.args_local.args[0].device == 'TM0'
    assert a.args_local.args[0].assign_string == 'TM0 = %s'
    assert a.args_local.args[1].device == 'TM2'
    assert a.args_local.args[1].assign_string == 'TM2 = %s'


def test_function_with_input():
    target = """
      function A: void
      var_input
          a0: WORD;
          a1: DWORD;
      end_var
      end_function
      """
    a = function.parseString(target)[0]
    assert isinstance(a, Function)
    assert a.name == 'A'
    assert a.ret_type == 'void'
    assert a.args_input.args[0].name == 'a0'
    assert a.args_input.args[0].type_string == 'WORD'
    assert a.args_input.args[1].name == 'a1'
    assert a.args_input.args[1].type_string == 'DWORD'
    assert a.size == 4
    env = Environment('TM', 0, 'Main')
    a.assign(env)
    assert a.args_input.args[0].device == 'TM0'
    assert a.args_input.args[0].assign_string == 'TM0 = %s'
    assert a.args_input.args[1].device == 'TM2'
    assert a.args_input.args[1].assign_string == 'TM2 = %s'


def test_function_with_input():
    target = """
      function A: void
      var_input
          a0: WORD;
          a1: DWORD;
      end_var
      var
          b0: WORD;
          b1: DWORD;
      end_var
      end_function
      """
    a = function.parseString(target)[0]
    assert isinstance(a, Function)
    assert a.name == 'A'
    assert a.ret_type == 'void'
    assert a.args_input.args[0].name == 'a0'
    assert a.args_input.args[0].type_string == 'WORD'
    assert a.args_input.args[1].name == 'a1'
    assert a.args_input.args[1].type_string == 'DWORD'
    assert a.args_local.args[0].name == 'b0'
    assert a.args_local.args[0].type_string == 'WORD'
    assert a.args_local.args[1].name == 'b1'
    assert a.args_local.args[1].type_string == 'DWORD'
    assert a.size == 8
    env = Environment('TM', 0, 'Main')
    a.assign(env)
    assert a.args_input.args[0].device == 'TM0'
    assert a.args_input.args[0].assign_string == 'TM0 = %s'
    assert a.args_input.args[1].device == 'TM2'
    assert a.args_input.args[1].assign_string == 'TM2 = %s'
    assert a.args_local.args[0].device == 'TM4'
    assert a.args_local.args[0].assign_string == 'TM4 = %s'
    assert a.args_local.args[1].device == 'TM6'
    assert a.args_local.args[1].assign_string == 'TM6 = %s'


def test_function_with_funcall_args():
    target = """
      function A: void
      var
          a0: WORD;
          a1: DWORD;
      end_var
      funcall B(a0, a1)
      end_function
      """
    a = function.parseString(target)[0]
    assert isinstance(a, Function)
    assert a.name == 'A'
    assert a.ret_type == 'void'
    assert isinstance(a.body[0], Funcall)
    assert a.body[0].name == 'B'
    assert a.body[0].args[0] == 'a0'
    assert a.body[0].args[1] == 'a1'


def test_function_with_funcall():
    target = """
      function A: void
      funcall B()
      end_function
      """
    a = function.parseString(target)[0]
    assert isinstance(a, Function)
    assert a.name == 'A'
    assert a.ret_type == 'void'
    assert isinstance(a.body[0], Funcall)
    assert a.body[0].name == 'B'


def test_function_with_body():
    target = """
      function A: void
      something
      end_function
      """
    a = function.parseString(target)[0]
    assert isinstance(a, Function)
    assert a.name == 'A'
    assert a.ret_type == 'void'
    assert a.body[0] == 'something'


def test_funcall():
    target = """
      funcall A()
    """
    expected = 'ECall("Main", A)'
    a = funcall.parseString(target)[0]
    assert isinstance(a, Funcall)
    assert a.name == 'A'
    assert len(a.args) == 0
    env = Environment('TM', 0, 'Main')
    f = Function('A', 'void', [], [], '')
    env.append_function(f)
    a.assign(env)
    assert a.converted == expected


def test_funcall_with_args():
    target = """
      funcall A(1, 2)
    """
    expected = """TM0 = 1
TM2 = 2
ECall("Main", A)"""
    a = funcall.parseString(target)[0]
    assert isinstance(a, Funcall)
    assert a.name == 'A'
    assert len(a.args) == 2
    env = Environment('TM', 0, 'Main')
    a1 = Arg('a1', 'WORD')
    a2 = Arg('a2', 'WORD')
    ai = ArgsInput([a1, a2])
    f = Function('A', 'void', [ai], [], '')
    f.assign(env)
    env.append_function(f)
    a.assign(env)
    assert a.converted == expected


"""
function B: void
    var input
        a1: WORD;
        a2: WORD;
        a3: WORD;
    end_var

    something

end_function

function A: void
    var_input
        a1: WORD;
        a2: WORD;
    end_var
    var
        b1: WORD;
        b2: WORD;
    end_var

    something
    funcall B(3, 4, 5);
    something

end_function
"""
