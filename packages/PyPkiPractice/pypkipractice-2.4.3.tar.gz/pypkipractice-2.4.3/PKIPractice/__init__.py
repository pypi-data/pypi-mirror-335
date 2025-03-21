"""
Top level entry point for the PyPKIPractice Program.

Methods:
    run_pki_practice - command line entry point to start the program and take in arguments.
"""

from .Utilities.CLIUtils import start_program


def run_pki_practice() -> None:
    """
    Command line entry point to start the program and take in arguments.
    """

    start_program()
