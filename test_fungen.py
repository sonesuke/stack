from fungen import *

import pep8
import glob


def test_pep8():
    pep8style = pep8.StyleGuide()
    result = pep8style.check_files(glob.glob('*.py'))
    assert result.total_errors == 0


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
    smoething

end_function
"""


def test_arg():
    target = "a1: WORD;"
    a = arg.parseString(target)[0]
    assert isinstance(a, Arg)
    assert a.name == 'a1'
    assert a.type_string == 'WORD'


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


def test_function():
    target = """
      function A: void
      end_function
      """
    a = function.parseString(target)[0]
    assert isinstance(a, Function)
    assert a.name == 'A'
    assert a.ret_type == 'void'


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


def test_function_with_local():
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
