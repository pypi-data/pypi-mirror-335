#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from typing import Union


from localecmd.func import Function, programfunction
from localecmd.module import Module


def remove_leading_chars(s: str, n_chars: int = 4):
    ret = ""
    for i, line in enumerate(s.split("\n")):
        if i == 0:
            ret += line
        else:
            ret += line[n_chars:] + "\n"
    return ret


def f_(x, y):
    return y


@programfunction()
def func(a: int = 9, *b: float, c: Union[int, str] = 8, **d: str):
    """
    This is a docstring

    This has many lines

    """
    # A function to use for testing, but should not be tested itself
    return "func"


@programfunction()
def func2(a: int = 9, b: float = 80, c: int = 8, d: float = 10):
    # A function to use for testing, but should not be tested itself
    return f"{a} {b} {c} {d}"


# Forget to use @programfunction


def funcerr(a=1):
    return 8


def test_test_functions():
    # Not needed, but testing coverage looks better then
    func()
    func2()
    funcerr()


def test_creation_errors():
    with pytest.raises(TypeError):
        Module("no-Function", [funcerr])


def test_properties():
    name = "Name"
    funcs = [func, func2]
    docstring = "The module docstring"
    mod = Module(name, funcs, docstring)

    assert mod.name == name
    assert mod._wrapped_module is None
    assert mod.exported_md == docstring
    assert mod.program_doc == docstring
    for i in range(len(funcs)):
        print(i, funcs[i].fname)
        assert mod.functions[i] == funcs[i]
        assert mod.functions[i].modulename == name


class test_module:
    "The module docstring"

    func = func
    func2 = func2


def test_from_module():
    mod = Module.from_module(test_module)
    assert mod.name == "test_module"
    assert mod.functions == [func, func2]
    assert mod._wrapped_module == test_module
    assert mod.exported_md == "The module docstring"
    assert mod.program_doc == "The module docstring"


class test_module2:
    "The module docstring"

    func = func
    func2 = func2
    funcerr = Function(funcerr)


def test_assign_docs(caplog):
    mod = Module.from_module(test_module2)
    mdoc = remove_leading_chars("""
    Module bla
    
    ### This is a header, but not for a function
    """)
    fdoc1 = remove_leading_chars("""
    ### func args... kwargs...
    Lorem ipsum dolor sit amet
    
    ### Examples
    Or not
    ### Some random header in correct level
    
    # Some header in wrong level
    
    """)
    fdoc2 = remove_leading_chars("""
    ### func2 something
    
    
    """)
    doc = "".join([mdoc, fdoc1, fdoc2])

    mod.assign_docs(doc, "###")
    assert "No loaded docs for funcerr" == caplog.record_tuples[-1][2]

    assert mod.program_doc == mdoc
    assert mod.functions[0].program_doc == fdoc1
    assert mod.functions[1].program_doc == fdoc2
