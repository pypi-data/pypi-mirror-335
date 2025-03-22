#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Class for
"""

import logging
import os
from typing import Union
from typing_extensions import Self

from localecmd.func import Function
from localecmd.localisation import DEFAULT_LOCALE_DIR

module_logger = logging.getLogger("Module")

DOCSTRING_LOCATION = "docs"
"Subfolder of <locale folder>/<language> that contains markdown helptexts"


class Module:
    """
    Implementing a module. That is a namespace for functions
    """

    def __init__(
        self, name: str, functions: list[Function], doc: Union[str, None] = None
    ) -> None:
        """
        Initialise module

        :param str name: Name of module
        :param list[Function] functions: List of functions that should belong to the module
        :param str doc: Docstring to show in the program and for export

        """
        self.name = name
        if doc is None:
            doc = ""
        self.set_program_doc(doc)
        self.__doc__ = doc
        self._wrapped_module = None
        self.functions = []
        # Assign module
        for i, function in enumerate(functions):
            if not isinstance(function, Function):
                msg = "The functions of the module must be Function objects, "
                msg += "but the {num}. element is not a Function".format(num=i + 1)
                msg += ". It is a {typ}".format(typ=str(type(function)))
                raise TypeError(msg)
            function.set_module(self)
            self.functions.append(function)

    @classmethod
    def from_module(cls, module) -> Self:
        """
        Turn python module into a Module object.

        This takes all {py:class}`Functions <zfp.cli.func.Function>` in the
        module as function list and the name from the module as name.
        """
        flist = []

        for data_name in dir(module):
            data = getattr(module, data_name)
            if isinstance(data, Function):
                flist.append(data)

        name = module.__name__.split(".")[-1]

        mod = cls(name, flist, module.__doc__)
        mod._wrapped_module = module
        mod.__doc__ == module.__doc__
        return mod

    @property
    def program_doc(self) -> str:
        """Module docstring to show in program"""
        return self.__translated_doc__

    def set_program_doc(self, s: str) -> None:
        """Set in-program module docstring"""
        module_logger.debug("Set docstring of module " + self.name)
        self.__translated_doc__ = s

    @property
    def exported_md(self) -> str:
        """Module docstring to export to sphinx documentation."""
        # This should be asserted already, but it seems that mypy didn't notice it
        assert isinstance(self.__doc__, str)

        return self.__doc__

    def load_docs_from_file(
        self,
        language: str,
        doc_folder: str = DEFAULT_LOCALE_DIR,
        doc_subfolder: str = DOCSTRING_LOCATION,
    ) -> str:  # pragma: no cover # io
        """Load docstrings for module and functions from file

        :param str language: In which language the docs shold be loaded in
        :param str doc_folder: In which folder to find docstrings. Defaults to `locale`.
        :param str doc_subfolder: Folder below doc_folder/language where to find the helptexts.
        The default is `docs`.
        :return: String containing the module doc file content in Markdown format
        :rtype: str

        The function will search for the file <doc_folder>/<language>/<doc_subfolder>/<module_name>.md
        """

        # If fallback, load English docstrings
        if not language:
            language = "en"

        msg = f"Loading docstrings for module {self.name} in language {language}"
        module_logger.debug(msg)

        # Load file
        folder = os.path.join(doc_folder, language, doc_subfolder)
        filepath = os.path.join(folder, self.name + ".md")
        if not os.path.isfile(filepath):
            msg = f"Could not find file {filepath}. No docstrings found"
            module_logger.warning(msg)
            return ""
        with open(filepath) as file:
            filelines = file.readlines()
        return "\n".join(filelines)

    def empty_docs(self) -> None:
        """
        Assign original Python docstrings of module and its functions.
        """
        self.set_program_doc('')
        for func in self.functions:
            func.set_program_doc('')

    def assign_docs(self, filelines: str, header_level: str = "###") -> None:
        """
        Parse file and assign the docstrings to the module and its functions.

        If the header is unknown, the lines are appended to the function before.
        This is because examples and notes have same header level, but also
        causes mistyped function names to be appended to the function before.

        :param str filelines: File content. Assuming markdown.
        :param str header_level: What characters appear between the newline
        and the function name. Default is '###' – markdown subsection header.

        """
        func_names = [f.translated_name for f in self.functions]
        docdict = {}
        module_docstring = ""
        current_function = ""

        sections = filelines.split(header_level)
        # Module does not start with ###
        # Module is not allowed to start directly on function docstring
        module_docstring += sections[0]
        for section in sections[1:]:
            # print('aaaaa\n', section, '\naaaaa\n')
            fname = section.split()[0]

            # If ### <function name> arrives
            if fname in func_names:
                msg = f"Finishing docstring for {current_function}"
                module_logger.debug(msg)

                current_function = fname
                msg = f"Starting on docstring for function {current_function}"
                module_logger.debug(msg)
                docdict[current_function] = ""
            # If ### <something else than function name>
            elif not current_function:
                module_docstring += header_level + section
                continue
            docdict[current_function] += header_level + section

        msg = f"Finishing docstring for function {current_function}"
        module_logger.debug(msg)
        # Actually assign
        self.set_program_doc(module_docstring)
        for i, fname in enumerate(func_names):
            if fname not in docdict:
                msg = f"No loaded docs for {fname}"
                module_logger.warning(msg)
                continue
            self.functions[i].set_program_doc(docdict[fname])
