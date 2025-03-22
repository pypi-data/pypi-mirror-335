#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import inspect

from typing import Union

from localecmd.func import (
    Function,
    programfunction,
    BRAILLE_PATTERN_BLANK,
)
from localecmd.localisation import f_


def dummy_f_(x, y):
    return y


def func(a: int = 9, *b: float, c: Union[int, str] = 8, **d: str):  # pragma: no cover
    """
    This is a docstring

    This has many lines

    """
    # A function to use for testing, but should not be tested itself
    return "func"


def func2(a: int = 9, b: float = 80, c: int = 8, d: float = 10):  # pragma: no cover
    # A function to use for testing, but should not be tested itself
    return f"{a} {b} {c} {d}"


def listf(a: list = 9):  # pragma: no cover  # Placeholder. No need to test
    # A function to use for testing, but should not be tested itself
    return "func"


def test_create_callstring():
    # Note that python allows atart to be a positional argument in bultin sum.
    f = Function(func, translate_function=dummy_f_)
    assert f.calling.strip() == "func a b... -c -d..."

    f = Function(func2, translate_function=dummy_f_)
    assert f.calling.strip() == "func2 a b c d"


def test_func():
    name = "haha"
    parameters = ["a", "b", "c", "d"]
    f = Function(func, name, translate_function=dummy_f_)
    # Show that properties are the same as of the wrapped function
    assert f.func == func
    assert f.__wrapped__ == func
    assert inspect.signature(f) == inspect.signature(func)
    assert f() == func()
    assert f.module.__name__ == __name__

    assert f.modulename == "test_func"
    assert f.fullname == "test_func.haha"
    assert f.fname == name
    assert f.translated_name == name
    assert f.name == "func"
    assert f.parameters == parameters
    assert f.f_ == dummy_f_

    f2 = Function(func, translate_function=dummy_f_)
    assert f2.modulename == "test_func"
    assert f2.fname == "func"
    assert f2.name == "func"
    assert f2.parameters == parameters

    # Test when no translation function is given
    f3 = Function(func)
    assert f3.modulename == "test_func"
    assert f3.fname == "func"
    assert f3.name == "func"
    assert f3.parameters == parameters
    assert f3.f_ == f_

    # Todo: Check non-valid translation functions


# def test_types():
#     name = "haha"
#     parameters = ["a", "b", "c", "d"]
#     f2 = Function(func2, name, translate_function=dummy_f_)
#     with pytest.raises(TypeMismatch):
#         f2(*parameters)


#     with pytest.raises(TypeError):
#         f2.convert_args(*parameters)

#     f = Function(func, translate_function=dummy_f_)
#     args, kwargs = f.convert_args('1', '2', '2', c='6', d='20.34')
#     assert args == (1, (2, 2))
#     assert kwargs == {'c': 6, 'd': 20.34}


def test_translation():
    # Test first that dict works
    # But need to test in English since translations may not be known.
    # Don't want to mess with the proper translations functions here
    name = "haha"
    # parameters = "a b c d".split()  # for clarity

    f = Function(func2, name, translate_function=lambda y, x: x.upper())

    paramdict = f.parameter_dictionary
    assert list(paramdict.keys()) == "A B C D".split()

    # Then overwrite that to see that translated call works
    args, kwargs = f.translate_call(A=10, B=20, C=30, D=40)
    assert kwargs == dict(zip('abcd', range(10, 50, 10)))


def test_wrapper():
    name = "haha"
    # parameters = "a b c d".split()  # for clarity

    f = Function(func, name, translate_function=dummy_f_)
    deco = programfunction(name, translate_function=dummy_f_)
    g = deco(func)

    assert f.func == g.func
    assert f.__wrapped__ == g.__wrapped__
    assert inspect.signature(f) == inspect.signature(g)
    assert f() == g()
    assert f.module.__name__ == g.module.__name__

    assert f.modulename == g.modulename
    assert f.translated_name == g.translated_name
    assert f.name == g.name
    assert f.fname == g.fname
    assert f.parameters == g.parameters


def test_docs():
    f1 = Function(func, "func", dummy_f_)
    f2 = Function(func2, "func2", dummy_f_)
    assert f1.oneliner == "This is a docstring"
    assert f2.oneliner == ""

    func2_doc = (
        ":::{py:function}"
        + f""" func a b... -c -d... {BRAILLE_PATTERN_BLANK}
        
        This is a docstring
    
        This has many lines
    
        :::
    """
    )
    assert f1.exported_md.split() == func2_doc.split()

    # Test the docstring seen within the program
    assert f1.program_doc.split() == func2_doc.split()[1:-1]
    # Now set the docs to something else and see if those have changed
    teststring = "### Hello, world\nhelloworld"
    f1.set_program_doc(teststring)
    assert f1.program_doc == teststring
    # And the oneliner should also ne changed
    assert f1.oneliner == "helloworld"
    # The oneliner should not have changed?
    # assert f.oneliner == teststring
