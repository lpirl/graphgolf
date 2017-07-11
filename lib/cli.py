"""
Contains the main CLI application and the top-level coordination of the
program.
"""

# encoding: UTF-8

from sys import argv
from os import getpid
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from logging import INFO, DEBUG, Formatter, getLogger, debug
from multiprocessing import Process

from lib.enhancers import EnhancerRegistry
from lib.graph_elements import GolfGraph
from lib.logging import AddPIDFilter

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
        self.best_graph = None

    def _init_arg_parser(self):
        self.arg_parser = ArgumentParser(
            description=("graph golf challenge experiments "
                         "(http://research.nii.ac.jp/graphgolf/)"),
            formatter_class=ArgumentDefaultsHelpFormatter,
        )
        self.arg_parser.add_argument('order', type=int,
                                     help="order of the graph")
        self.arg_parser.add_argument('degree', type=int,
                                     help="degree of the graph")

    def _init_enhancers(self):
        enhancer_classes = EnhancerRegistry.enhancers
        debug("initializing enhancers %r", enhancer_classes)
        self.enhancers = [Enhancer(self.arg_parser)
                          for Enhancer in enhancer_classes]

    def _init_logging(self):
        self.arg_parser.add_argument('-d', '--debug', action='store_true',
                                     default=False,
                                     help='turn on debug messages')
        self.arg_parser.add_argument('-v', '--verbose', action='store_true',
                                     default=False,
                                     help='turn on verbose messages')

        formatter = Formatter("%(levelname)s:%(process)d:%(message)s")

        logger = getLogger()
        logger.name = "woods"

        for handler in logger.handlers:
            handler.setFormatter(formatter)

    def run(self):
        """
        This kicks off the actual operation (i.e. use the users' args,
        options and sub commands to server the request).

        Once an enhanced graph could be determined, we kill the other
        enhancers and restart them on the enhanced graph.
        """
        debug("starting to run")

        self._parse_args()

        # create initial graph
        initial_graph = GolfGraph(self.args.order, self.args.degree)
        initial_graph.add_as_many_random_edges_as_possible()
        initial_graph.analyze()
        print("initial 'best' graph:", initial_graph)
        self.best_graph = initial_graph
        self._run(self.enhancers[0])

    def _run(self, my_enhancer):
        """
        Runs ``enhancer`` in this process and the other enhancers in
        forked processes.
        In case ``enhancer`` finishes, it kills and re-forks the others.
        """

        # create other processes
        other_processes = [
            Process(target=enhancer.enhance, args=(self.best_graph,))
            for enhancer in self.enhancers
            if not enhancer == my_enhancer
        ]

        # start other processes
        for process in other_processes:
            process.start()
            debug("started %s", process.pid)

        # start my enhancer
        self.best_graph = my_enhancer.enhance(self.best_graph)

        if self.best_graph:
            debug("%i found a better graph", getpid())
            for process in other_processes:
                process.terminate()
                debug("terminated %s", process.pid)
            self._run(my_enhancer)

        # We did not find a enhanced graph, so we just wait for the
        # other processes.
        # The following loop should only finish if all enhancers gave up
        # finding a better graph (what should never happen), so we
        # probably/hopefully get killed while waiting for the others.
        debug("parent waits for children")
        for process in other_processes:
            process.join()

        assert False, "all enhancers gave up - this should never happen"


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
