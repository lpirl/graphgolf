from test import BaseTest

from lib.graph_elements import GolfGraph, Node, Edge

class EdgeTest(BaseTest):
    """
    Tests class ``Edge``.
    """

    def test_order(self):
        """
        Tests whether nodes of edges are ordered.
        """
        n1 = Node(1)
        n2 = Node(2)
        e1 = Edge(n1, n2)
        e2 = Edge(n2, n1)
        self.assertEqual(e1.a, e2.a)
        self.assertEqual(e1.b, e2.b)

class GolfGraphTest(BaseTest):
    """
    Tests various graph operations.
    """

    def setUp(self):
        self.order = 32
        self.graph = GolfGraph(self.order)

    def test_graph_creation(self):
        """
        Tests if all nodes are created correctly.
        """

        # no initial edges
        self.assertFalse(self.graph.edges)

        # all initial nodes
        nodes = self.graph.nodes
        for x in range(self.order):
          self.assertIn(Node(x), nodes)
