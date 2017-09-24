"""
Tests various CLI operations.
"""

from sys import argv
from os import remove

from test import BaseTest
from lib.cli import Cli
from lib.graph_elements import GolfGraph

class CliTest(BaseTest):
    """
    See module docstring.
    """

    def setUp(self):
        """
        Initialized commonly needed objects.
        """
        self.cli = Cli()

    def test_write_out_and_read_in(self):
        """
        Test writing and reading of persisted graphs (i.e., plain text
        files containing a list of edges).
        """
        orders_degrees = ((5, 4), (10, 9), (10, 11))
        for order, degree in orders_degrees:
            self.cli.best_graph = GolfGraph(order, degree)
            self.cli.best_graph.add_as_many_random_edges_as_possible()
            self.cli.best_graph.analyze()
            filename = self.cli.current_edges_filename()
            self.cli.write_edges()

            cli = Cli()
            cli.best_graph = GolfGraph(order, degree)
            cli.load_edges(filename)
            cli.best_graph.analyze()

            for attr_name in ("order", "degree", "aspl", "diameter"):
                self.assertEqual(
                    getattr(cli.best_graph, attr_name),
                    getattr(self.cli.best_graph, attr_name)
                )

            remove(filename)
