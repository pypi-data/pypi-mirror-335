from localecmd import start_cli
import functions
from functions import _, DOMAIN


def main():
    modules = [functions]
    greeting = _("Welcome to the turtle shell. Type help to list commands.")
    cli = start_cli(modules, greeting=greeting, gettext_domains=[DOMAIN])
    cli.cmdloop()
    cli.close()


main()
