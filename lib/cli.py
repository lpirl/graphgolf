"""
Contains the main CLI application and the top-level coordination of the
program.
"""

# encoding: UTF-8

from sys import argv
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import logging

class Cli(object):
    """
    Implements top-level coordination and interaction as CLI.

    After initialization, all you need is ``run()``.
    """

    def __init__(self):
        """
        Finds/loads/initializes everything needed for operation.
        """
        # enabling debugging is the first thing we (might) have to do:
        if '-d' in argv or '--debug' in argv:
            logging.getLogger().setLevel(logging.DEBUG)

        logging.debug("initializing CLI")

        self.targets = None
        """
        The set of all known targets.
        """

        self.detected_targets = None
        """
        The set of all (i.e. directly) detected targets.
        """

        self.implied_targets = None
        """
        The set of all implied targets (through detected ones).
        """

        self.injectors = None
        """
        The set of all known injectors.
        """

        self._init_arg_parser()
        self._init_logging()
        self.args = None

    def _init_arg_parser(self):
        self.arg_parser = ArgumentParser(
            description=("graph golf challenge experiments "
                         "(http://research.nii.ac.jp/graphgolf/)"),
            formatter_class=ArgumentDefaultsHelpFormatter,
        )

    def _init_logging(self):
        logging.getLogger().name = "fiad"
        self.arg_parser.add_argument('-d', '--debug', action='store_true',
                                     default=False,
                                     help='turn on debug messages')
        self.arg_parser.add_argument('-v', '--verbose', action='store_true',
                                     default=False,
                                     help='turn on verbose messages')
        self.arg_parser.add_argument('n', type=int,
                                     help="order of the graph")
        self.arg_parser.add_argument('d', type=int,
                                     help="degree of the graph")

    def run(self):
        """
        This kicks off the actual operation (i.e. use the users' args,
        options and sub commands to server the request).
        """
        logging.debug("starting to run")

        self._parse_args()
        raise NotImplementedError()

    def _parse_args(self):
        logging.debug("parsing command line arguments")

        # display help per default:
        if len(argv) == 1:
            argv.append("-h")

        self.args = self.arg_parser.parse_args()

        if self.args.verbose:
            logging.getLogger().setLevel(logging.INFO)

        if self.args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
