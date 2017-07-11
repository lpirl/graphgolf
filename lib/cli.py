"""
Contains the main CLI application and the top-level coordination of the
program.
"""

# encoding: UTF-8

from sys import argv
from os import getpid, fork, waitpid, kill
from signal import SIGKILL
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from logging import INFO, DEBUG, Formatter, getLogger, debug, info
from multiprocessing import Array as SharedArray

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
        self._init_logging()
        self._init_enhancers()
        self.args = None
        self.best_graph = None
        self.controller_pid = None
        self.children_pids = None

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

    @property
    def is_controller(self):
        """
        Returns whether this (instance in this) process is the controller
        process.
        """
        return getpid() == self.controller_pid

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

    def run(self):
        """
        This initially kicks off the actual operation.
        """
        debug("starting to run")
        self._parse_args()
        self.children_pids = SharedArray("i", len(self.enhancers))
        graph = GolfGraph(self.args.order, self.args.degree)
        graph.add_as_many_random_edges_as_possible()
        graph.analyze()
        print("initial graph:", graph)
        self.best_graph = graph

        self._control()

    def _control(self):
        """
        Does what a controller does: fork working children, and  wait
        for them to finish.
        The child that first finds an enhanced graphs takes over the role
        of the controller.
        This avoids inter-process communication by copying the graph via
        ``fork()``.
        """
        # ``while True`` avoids infinite recursions of ``_control``.
        while True:
            self.controller_pid = getpid()
            for child_i, enhancer in enumerate(self.enhancers[:]):

                #############################
                # code for controller process
                #
                child_pid = fork()
                if child_pid:
                    self.children_pids[child_i] = child_pid
                    continue
                assert self.is_controller is False
                #
                #############################

                #############################
                # code for child process
                #
                self.best_graph = enhancer.enhance(self.best_graph)
                if not self.best_graph:
                    info("exited without finding a better graph")
                    self.enhancers.remove(enhancer)
                    self.children_pids[child_i] = 0
                    exit(0)

                for child_i_to_kill, pid in enumerate(self.children_pids):
                    if pid == 0:
                        # already dead
                        continue
                    elif child_i != child_i_to_kill:
                        debug("child kills sibling %i", pid)
                        self.children_pids[child_i_to_kill] = 0
                        kill(pid, SIGKILL)

                # by breaking this (controller) loop (as child), we
                # basically take over control
                break
                #
                #############################

            # controller spawned all processes
            if self.is_controller:
                #~ for pid in self.children_pids:
                    #~ if pid:
                        #~ debug("controller waits for child %i", pid)
                        #~ waitpid(pid, 0)
                exit(0)

    #~ def exit(self, code=0):
        #~ """
        #~ Makes sure own PID is not present in ``children_pids`` and exits.
        #~ """
        #~ pid = getpid()
        #~ for child_i in len(self.enhancers):
            #~ if self.children_pids[child_i] == pid:
                #~ self.children_pids[child_i] = None
        #~ exit(code)
