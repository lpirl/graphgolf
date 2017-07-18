"""
Contains the main CLI application and the top-level coordination of the
program.
"""

# encoding: UTF-8

from sys import argv
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from logging import INFO, DEBUG, Formatter, getLogger, debug, info
from multiprocessing import Process, Manager

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

    def _init_arg_parser(self):
        self.arg_parser = ArgumentParser(
            description=("graph golf challenge experiments "
                         "(http://research.nii.ac.jp/graphgolf/)"),
            formatter_class=ArgumentDefaultsHelpFormatter,
        )
        self.arg_parser.add_argument('-e', '--edges', type=str,
                                     help="file name to load edges from")
        self.arg_parser.add_argument('-s', '--serial', action='store_true',
                                     default=False,
                                     help=("serial "
                                           "execution for debugging (** "
                                           "W/O MAKING ACTUAL PROGRESS**)"))
        self.arg_parser.add_argument('-o', '--once', action='store_true',
                                     default=False,
                                     help="run enhancers only once")
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

        self.best_graph = GolfGraph(self.args.order, self.args.degree)
        if self.args.edges:
            self.load_edges()
        else:
            self.best_graph.add_as_many_random_edges_as_possible()

        print("lower bound diameter:",
              self.best_graph.diameter_lower_bound)
        print("lower bound average shortest path length:",
              self.best_graph.aspl_lower_bound)

        self.best_graph.analyze()
        print("initial graph:", self.best_graph)

        try:
            if self.args.serial:
                self._run_debug()
            else:
                self._run()
        except KeyboardInterrupt:
            self.write_edges()

    def _run(self):
        """
        Tries to enhance the ``self.best_graph`` forever.
        Once an enhancer returns an enhanced graph, all enhancers are
        restarted therewith.
        """

        processes = []
        report_queue = Manager().Queue()

        while True:

            # create processes
            for enhancer in self.enhancers:
                if enhancer.applicable_to(self.best_graph):
                    processes.append(
                        Process(target=enhancer.enhance,
                                args=(self.best_graph, report_queue))
                    )

            # start processes
            for process in processes:
                debug("starting %s", process)
                process.start()

            # wait for any of them
            self.best_graph = report_queue.get()
            print(self.best_graph)

            # kill the rest
            while processes:
                process = processes.pop()
                debug("terminating %s", process)
                process.terminate()

            # in case processes submitted a graph before they got killed
            while not report_queue.empty():
                report_queue.get()

            if self.args.once:
                break

    def _run_debug(self):
        """
        Like ``_run`` but w/o forking processes and parallelism.
        **MAKES NO ACTUAL PROGRESS**
        """
        report_queue = Manager().Queue()
        while True:
            for enhancer in self.enhancers:
                if enhancer.applicable_to(self.best_graph):
                    enhancer.enhance(self.best_graph, report_queue)

            if self.args.once:
                break

    def current_edges_filename(self):
        """
        Returns the file name of the current edges file.
        """

        assert self.best_graph.diameter is not None
        assert self.best_graph.aspl is not None

        return "-".join((
            "edges",
            "order=%i" % self.best_graph.order,
            "degree=%i" % self.best_graph.degree,
            "diameter=%i" % self.best_graph.diameter,
            "aspl=%f" % self.best_graph.aspl
        ))

    def write_edges(self):
        """
        Writes the best graph to a file.

        #refactoring: maybe this should be moved to another/separate class?
        """
        assert self.best_graph.diameter is not None
        assert self.best_graph.aspl is not None

        info("writing out best graph found")

        with open(self.current_edges_filename(), mode="w") as open_file:
            open_file.writelines(("%i %i\n" % (v1.id, v2.id)
                                  for v1, v2 in self.best_graph.edges()))

    def load_edges(self):
        """
        Loads edges form the file specified in ``self.args`` into
        ``self.best_graph``.

        #refactoring: maybe this should be moved to another/separate class?
        """
        with open(self.args.edges, "r") as open_file:
            for line in open_file.readlines():
                line = line.strip()
                vertex_a_id, vertex_b_id = line.split(" ")
                self.best_graph.add_edge_unsafe(
                    self.best_graph.vertices[int(vertex_a_id)],
                    self.best_graph.vertices[int(vertex_b_id)],
                )
