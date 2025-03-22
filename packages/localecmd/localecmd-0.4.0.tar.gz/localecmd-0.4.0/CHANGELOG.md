## 0.4.0 (2025-03-22)

### New features

- Keyword arguments can now contain more than one argument per keyword

### Changes

- Type of arguments is now converted with function annotations (#2)

## 0.3.0 (2025-03-09)

### New features

- Allow handling of more domains than the internal ones

### Changes

- Switch to babel for gettext domain handling and language switching

## 0.2.0 (2025-03-06)

### New features

- Function to create all pot files at once
- Export module directly to library users
- Function t o run scripts
- Addability to optionally run commands in system/fallback language (typically english)
- **Function**: Give default translator function by library
- **Cli**: Allow to run commands directly with cli.runcmd
- **Cli**: Allow loading module objects in addition to modules
- **Pot**: Generate pot file for localecmd messages
- **Type-translation**: Create type list automatically
- **Pot**: Add function to generate pot files o ffunction names and parameters
- **Cli**: Add function to restart cli to start it even if it is running
- **Cli**: Include builtin functions and enable them by default
- Make important parts of library easier accessible

### Fixes

- **Parsing**: Negative numbers are not longer interpreted as keyword arguments
- **Parsing**: Solve name conflicts between function and distributor
- Load correct docstrings
- Markdown needs double newline to generate a newline and added missing type annotation
- **Docstrings**: Only show myst syntax in myst export
- Fix typing and removed missing imports
- **Cli**: Ensure that translators are enabled every time the cli starts
- Fix errors detected by mypy
- Stop overriding cli attributes when one tries to create second cli

### Changes

- Change default docstring folder
- Log executed commands
- Don't add space after command run
- Start_cli now retuns cli object
- **Pot**: Centralise pot file saving
- **Cli**: Closing cli now needs access to cli object
- **Cli**: Move cmdloop to method of cli but keep a wrapper of it
- **Cli**: Move static functions out of class
- Simplify calling
- **Function-translation**: Reorder if statements for better understanding
- **Language-switching**: Simplify fallback handling
