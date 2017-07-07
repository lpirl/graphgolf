"""
Contains the main CLI application and the top-level coordination of the
program.
"""

# encoding: UTF-8

from sys import argv
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from logging import INFO, DEBUG, getLogger, debug
from multiprocessing import Process

from lib.enhancers import EnhancerRegistry
from lib.graph_elements import GolfGraph

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
            getLogger().setLevel(DEBUG)

        debug("initializing CLI")

        self.enahncers = None
        """
        All initialized enhancers.
        """

        self._init_arg_parser()
        self._init_enhancers()
        self._init_logging()
        self.args = None

    def _init_arg_parser(self):

        self.arg_parser = ArgumentParser(
            description=("graph golf challenge experiments "
                         "(http://research.nii.ac.jp/graphgolf/)"),
            formatter_class=ArgumentDefaultsHelpFormatter,
        )

    def _init_enhancers(self):
        enhancer_classes = EnhancerRegistry.enhancers
        debug("initializing enhancers %r", enhancer_classes)
        self.enhancers = [Enhancer(self.arg_parser)
                          for Enhancer in enhancer_classes]

    def _init_logging(self):
        getLogger().name = "woods"
        self.arg_parser.add_argument('-d', '--debug', action='store_true',
                                     default=False,
                                     help='turn on debug messages')
        self.arg_parser.add_argument('-v', '--verbose', action='store_true',
                                     default=False,
                                     help='turn on verbose messages')
        self.arg_parser.add_argument('order', type=int,
                                     help="order of the graph")
        self.arg_parser.add_argument('degree', type=int,
                                     help="degree of the graph")

    def run(self):
        """
        This kicks off the actual operation (i.e. use the users' args,
        options and sub commands to server the request).
        """
        debug("starting to run")

        self._parse_args()

        # create initial graph
        initial_graph = GolfGraph(self.args.order, self.args.degree)
        initial_graph.add_as_many_random_edges_as_possible()
        initial_graph.analyze()
        print("intial graph:", initial_graph)

        # create, start, and join processes
        processes = [Process(target=enhancer.run, args=(initial_graph,))
                     for enhancer in self.enhancers]
        for process in processes:
            process.start()
        for process in processes:
            process.join()

    def _parse_args(self):
        debug("parsing command line arguments")

        # display help per default:
        if len(argv) == 1:
            argv.append("-h")

        self.args = self.arg_parser.parse_args()

        if self.args.verbose:
            getLogger().setLevel(INFO)

        if self.args.debug:
            getLogger().setLevel(DEBUG)
