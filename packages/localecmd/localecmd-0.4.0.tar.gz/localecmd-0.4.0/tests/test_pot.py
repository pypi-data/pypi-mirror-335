import datetime
from io import StringIO
import os
import tempfile
from typing import Union

from babel.util import LOCALTZ
from babel.messages.pofile import read_po

from localecmd import pot
from localecmd.func import Function
from localecmd.localisation import f_, CLI_DOMAIN, FUNCTION_DOMAIN, TYPE_DOMAIN


def help(
    *args: str, kwarg: Union[int, str]
):  # pragma: no cover  # Placeholder. No need to test
    print(*args)


def quit(*args: int):  # pragma: no cover  # Placeholder. No need to test
    raise SystemExit


class module:
    help = Function(help, "help", f_)
    quit = Function(quit, "quit", f_)


potfile = rf"""# Translations template for test_pot.
# Copyright (C) 2025 ORGANIZATION
# This file is distributed under the same license as the test_pot project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2025.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: test_pot v0.1.0\n"
"Report-Msgid-Bugs-To: user@example.com\n"
"POT-Creation-Date: {datetime.datetime.now(LOCALTZ):%Y-%m-%d %H:%M%z}\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Generated-By: Babel 2.17.0\n"

# Function
msgctxt "test_pot"
msgid "help"
msgstr ""

# Parameter
msgctxt "test_pot.help"
msgid "args"
msgstr ""

# Parameter
msgctxt "test_pot.help"
msgid "kwarg"
msgstr ""

# Function
msgctxt "test_pot"
msgid "quit"
msgstr ""

# Parameter
msgctxt "test_pot.quit"
msgid "args"
msgstr ""

"""


def test_functions_pot():
    with tempfile.TemporaryDirectory() as tmpdirname:
        pot.create_functions_pot(
            [module.help, module.quit],
            tmpdirname,
            "test_pot",
            "v0.1.0",
            address="user@example.com",
        )

        with open(os.path.join(tmpdirname, FUNCTION_DOMAIN + '.pot')) as file:
            assert file.read() == potfile


typepotfile = rf"""# Translations template for test_pot.
# Copyright (C) 2025 ORGANIZATION
# This file is distributed under the same license as the test_pot project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2025.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: test_pot v0.1.0\n"
"Report-Msgid-Bugs-To: user@example.com\n"
"POT-Creation-Date: {datetime.datetime.now(LOCALTZ):%Y-%m-%d %H:%M%z}\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Generated-By: Babel 2.17.0\n"

#: tests.test_pot:15
msgid "str"
msgstr ""

#: tests.test_pot:15 tests.test_pot:21
msgid "int"
msgstr ""

"""


def test_types_pot():
    with tempfile.TemporaryDirectory() as tmpdirname:
        pot.create_types_pot(
            [module.help, module.quit],
            tmpdirname,
            "test_pot",
            "v0.1.0",
            address="user@example.com",
        )

        with open(os.path.join(tmpdirname, TYPE_DOMAIN + '.pot')) as file:
            assert file.read() == typepotfile


def test_messages_pot():
    with tempfile.TemporaryDirectory() as tmpdirname:
        pot.create_messages_pot(
            tmpdirname, "test_pot", "v0.1.0", address="user@example.com"
        )
        with open(os.path.join(tmpdirname, CLI_DOMAIN + '.pot')) as file:
            buf = StringIO(file.read())
            assert not [error for error in read_po(buf).check()]
