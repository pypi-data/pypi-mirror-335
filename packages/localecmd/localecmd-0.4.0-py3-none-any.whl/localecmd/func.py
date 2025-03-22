# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from localecmd.doc_translation import translate_examples, translate_parameters
from localecmd.localisation import f_
from typing import Callable, Union
import logging
import inspect


BRAILLE_PATTERN_BLANK = "⠀"

module_logger = logging.getLogger("Function")


class Function:
    """
    Function callable from the CLI.

    This is a wrapper around the python builtin function with the advantage that
    function name, parameters and types can be translated. It adds some properties
    that are useful for translation.

    Attributes `__name__` and `__doc__` are left unchanged. To access the shown
    name, use {py:attr}`Function.name` (untranslated) or
    {py:attr}`Function.translated_name`.

    To call the function from python, use the function as every other function.
    Then, args and kwargs are passed directly.

    :param Callable func: The original function
    :param str fname: Untranslated name as it will be shown in the program
    :param list[str] parameters: Untranslated function parameters
    """

    def __init__(
        self,
        func: Callable,
        name: str = "",
        translate_function: Union[Callable, None] = None,
    ) -> None:
        """
        Initialize function.

        :param Callable func: Actual function that will be called
        :param str name: Name of the function as shown in program.
        If empty, the name will be as shown in python.
        :param Callable | None translate_function: Function to translate function
        name and parameter names. For more information, see below.
        Defaults to None.

        The function to translate the name and parameters can be given in three ways:
        1. Provided as argument when decorating the function with
        {py:func}`localecmd.func.programfunction` or {py:func}`localecmd.func.Function`
        2. As a function `f_` in the module the function is in.
        3. The default function {py:func}`localecmd.localisation.f_`


        The translation function must take two arguments: First the context,
        then the string to translate.
        For functions, the context is the module name, for parameter names, this
        is `<module name>.<funcion name>`.
        """

        # Mypy likes this
        assert inspect.isfunction(func)

        self.func = func

        # Tell Python where to find signature, annotations etc.
        self.__wrapped__ = func

        # Keep name and doc
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

        # For translation
        self.__translated_doc__ = ""

        # Function name in the program
        if name:
            self.fname = name
        else:
            self.fname = func.__name__

        self.signature = inspect.signature(func)
        # Function parameters
        self.parameters = list(self.signature.parameters.keys())

        self._inspect_module()

        # Translate function
        if translate_function is not None:  # Should be: is callable
            # Todo: Check that this function is valid and takes two parameters
            msg = "Use passed translator function to translate {fullname}"
            module_logger.debug(msg)
            self.f_ = translate_function
        elif hasattr(self.module, "f_"):
            # Todo: inspect self.module.f_ that it is a valid function with two parameters
            msg = "Use translator function in module {self.modulename} to translate {fullname}"
            module_logger.debug(msg)
            self.f_ = self.module.f_
        else:
            msg = "Use default translator function to translate {fullname}"
            module_logger.debug(msg)
            self.f_ = f_

        # Remember to change/add user docs as func.__doc__ is API...

    def __call__(self, *args, **kwargs):
        """
        Call wrapped function directly.

        raises TypeMismatch: If type of arguments does not comply with function type annotations.
        """
        # Todo: Add logging
        return self.func.__call__(*args, **kwargs)

    def translate_call(self, *args, **kwargs):
        # Translate kwargs
        kwargs = {self.parameter_dictionary[k]: v for k, v in kwargs.items()}

        return args, kwargs

    @property
    def translated_name(self) -> str:
        """Translated name"""
        # Remember to translate...
        return self.f_(self.modulename, self.fname)

    @property
    def doc(self) -> str:
        """Untranslated docstring of function, but with removed indenting."""
        s = ""
        if self.__doc__ is not None:
            s = inspect.cleandoc(self.__doc__)
        return s

    @property
    def program_doc(self) -> str:
        """Function docstring to show in program"""
        if self.__translated_doc__:
            return self.__translated_doc__
        else:
            msg = "No translated doc loaded. Converts the raw one."
            module_logger.info(msg)
            return self.converted_docstring

    def set_program_doc(self, doc: str) -> None:
        """Replace translated docstring with `doc`"""
        self.__translated_doc__ = str(doc)

    @property
    def converted_docstring(self) -> str:
        """Convert docstring of function with all names translated.

        To show to user and export to sphinx documentation
        """
        # character BRAILLE PATTERN BLANK is to hide the parentheses that python functions use
        docheader = f"{self.calling}" + BRAILLE_PATTERN_BLANK + '\n\n'
        docbody = translate_examples(
            translate_parameters(self.doc, self.fullname),
            self.translated_name,
            self.fullname,
        )
        return docheader + docbody

    @property
    def exported_md(self) -> str:
        """Docstring of function with function, parameter and type names translated.

        For export to sphinx documentation
        """
        return ":::{py:function} " + self.converted_docstring + "\n:::"

    @property
    def oneliner(self) -> str:
        """First line of docstring that shortly describes what the function does"""
        # Finds first line in markdown document that contatins something and is not a heading
        if self.__translated_doc__:
            # Loop below will never complete because of return statement at first opportunity
            for line in self.__translated_doc__.split("\n"):  # pragma: no branch
                if line and not line.startswith("#"):
                    return line
        # Or if it is just a python docstring, it is the first line
        lines = self.doc.split("\n")
        return lines[0]

    @property
    def calling(self) -> str:
        """Generate signature of function

        Signature is on the form\n
        func positional args... -kwarg1 -kwargs...
        """
        s = self.translated_name + " "
        sig = inspect.signature(self)

        for p in sig.parameters.values():
            if p.kind in [
                inspect.Parameter.KEYWORD_ONLY,
                inspect.Parameter.VAR_KEYWORD,
            ]:
                s += "-"
            s += self.f_(self.fullname, p.name)
            if p.kind == inspect.Parameter.VAR_POSITIONAL:
                s += "..."
            if p.kind == inspect.Parameter.VAR_KEYWORD:
                s += "..."
            s += " "
        return s

    @property
    def parameter_dictionary(self) -> dict[str, str]:
        """Dictionary with translated -> untranslated parameter names

        :rtype: dict[str, str]

        """
        return {self.f_(self.fullname, p): p for p in self.parameters}

    @property
    def name(self) -> str:
        """Name of wrapped function"""
        # Remember to translate...
        return self.__name__

    @property
    def fullname(self) -> str:
        """Untranslated name with module as prefix"""
        return self.modulename + "." + self.fname

    # Is useful for checking, but could we use inspect.getmodule(self)?
    @property
    def module(self):
        "Python module the function was in"
        return self._module

    # Is useful for sorting
    @property
    def modulename(self) -> str:
        "Name of the module the function was in without path"
        return self._modulename

    def _inspect_module(self) -> None:
        """
        Set module and modulename properties by inspecting the wrapped function
        """
        # Set the module. Do it there so it can be overwritten.
        # Need to overwrite module and modulename for testing to not get
        # Heisenbugs because when testing, all modules are __main__...,
        # but the _correct_ module name (not __main__) is needed to test the
        # translation
        module = inspect.getmodule(self.func)
        assert inspect.ismodule(module)
        self._module = module
        self._modulename = self.module.__name__.split(".")[-1]

    def set_module(self, module) -> None:
        """
        Set module and modulename properties explicitly.

        :param Module module: {py:class}`zfp.cli.module.Module` this function belongs to.

        """
        # Sadly, can't test instance because we can't load Module module here
        # As that would be a circular import.
        assert module.__class__.__name__ == "Module"
        self._module = module
        self._modulename = module.name


def programfunction(
    name: str = "", translate_function: Union[Callable, None] = None
) -> Callable:
    """
    Wrap function such that it becomes a {py:class}`Function`.

    The decorator must be used with parentheses also when no arguments are passed:
    :::{code} python
    @programfunction()
    def some_function():
        (...)
    :::
    See {py:class}`there <Function>` under Initialization for argument description.

    """

    def decorator(func: Callable) -> Function:
        f = Function(func, name, translate_function)
        return f

    return decorator
