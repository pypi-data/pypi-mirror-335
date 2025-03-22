#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
General functions in a command-line program.
"""

from localecmd.cli import CLI, change_cli_language
from localecmd.func import programfunction
from localecmd.localisation import _, f_, language_list

from rich.markdown import Markdown
from rich.table import Table
from rich import print as rprint


__translator_function__ = f_  # This line disables W0611


@programfunction()
def help(*topic: str):
    """Get help

    :param str topic: Function/Topic to get help on. If empty, a list of all
    functions and topics is shown.

    :::{rubric} Examples
    :::
    :::{code} python
    Show list of all functions and topics
    >>> help()
    (...)
    Show helptext on function help.
    >>> help('help')
    (...)
    :::
    """

    functions = CLI.functions

    if not topic:
        # Print list of all functions
        table = Table(title=_("Available commands:"))
        table.add_column(_("command"), justify='left')
        table.add_column(_("description"), justify='left')

        for fname, func in functions.items():
            table.add_row(fname, func.oneliner)
        rprint(table)
    elif topic[0] in functions.keys():
        # Print docstring of one function
        func = functions[topic[0]]
        rprint(Markdown(func.program_doc))
    else:
        print(_("Command {0} does not exist!").format(topic[0]))


@programfunction()
def quit():
    """Terminate program

    :raises SystemExit: Always
    """
    raise SystemExit


@programfunction()
def change_language(language: str = ""):
    """Change language of program

    :param str language: Folder name containing the translation strings.
    Must be subfolder of folder specified by CLI.localedir.
    Defaults to '' meaning the fallback language English.
    """
    change_cli_language(language)


@programfunction()
def list_languages() -> None:
    """Print list of available program languages"""
    langs = language_list(include_fallback=True)
    table = Table(title=_("Supported languages in command line:"))
    table.add_column(_("Language code"), justify='left')
    table.add_column(_("Language name"), justify='left')
    for code in langs:
        table.add_row(code, code)  # Todo: reinsert the language name
    rprint(table)
    print()
    print(_('To change the language, type "change_language <language code>"'))
