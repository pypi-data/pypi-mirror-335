#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pytest
import tempfile

from babel.messages.catalog import Catalog
from babel.messages.mofile import write_mo


from localecmd.cli import CLI
from localecmd import builtins
from localecmd.localisation import DOMAIN_LIST


def test_help(capsys):
    # Start CLI first, if not done already
    assert not CLI.running
    cli = CLI([builtins])

    # Startup messages
    capsys.readouterr().out

    builtins.help()
    help_words = capsys.readouterr().out.strip()
    assert help_words.startswith("Available commands")
    assert "help" in help_words
    assert "quit" in help_words

    builtins.help("help")
    assert "help topic" in capsys.readouterr().out.strip()

    builtins.help("aojeg")
    assert capsys.readouterr().out.strip() == "Command aojeg does not exist!"

    cli.close()


def test_quit():
    with pytest.raises(SystemExit):
        builtins.quit()


def create_mo(domain, lang, folder):
    catalog = Catalog()
    # Bad style. Should remove lang from calling, but want to be flexible
    assert lang == "de_DE"
    catalog.add("help", "hilfe", context="builtins", locations=[("test.py", 42)])
    catalog.add("quit", "schließen", context="builtins", locations=[("test.py", 815)])

    path = os.path.join(folder, lang, "LC_MESSAGES")
    os.makedirs(path, exist_ok=True)

    filename = os.path.join(path, domain + ".mo")
    print(filename)

    with open(filename, "wb") as mo:
        write_mo(mo, catalog)


def test_change_language():
    # Create temporary localisation file
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdirname = tempfile.TemporaryDirectory().name
        print(tmpdirname)
        lang = "de_DE"
        # Must have all three to enable translation
        for domain in DOMAIN_LIST:
            create_mo(domain, lang, tmpdirname)

        # Start CLI first, if not done already
        cli = CLI([builtins], localedir=tmpdirname)

        assert "help" in cli.functions.keys()
        assert "hilfe" not in cli.functions.keys()

        assert cli.language == ''

        builtins.change_language("de_DE")

        assert "help" not in cli.functions.keys()
        assert "hilfe" in cli.functions.keys()

        assert cli.language == 'de_DE'

        # Should not change anything
        builtins.change_language("abc")

        assert "help" not in cli.functions.keys()
        assert "hilfe" in cli.functions.keys()

        assert cli.language == 'de_DE'

        # Must change back for other tests to work.
        builtins.change_language("")

    cli.close()


def test_list_languages(capsys):
    # Start CLI first, if not done already
    # if CLI.running:
    #     cli = CLI.get_cli()
    #     cli.close()
    cli = CLI([builtins])
    builtins.list_languages()
    printed = capsys.readouterr().out
    assert 'fallback' in printed  # Cant really expect more...
    cli.close()
