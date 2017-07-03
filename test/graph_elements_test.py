from test import BaseTest

from lib.graph_elements import GolfGraph, Vertex

class VertexTest(BaseTest):
    """
    Tests class ``Vertex``.
    """

    def setUp(self):
        self.v1 = Vertex(1, 1)
        self.v2 = Vertex(2, 1)
        self.v3 = Vertex(3, 1)

    def test_order(self):
        """
        Tests whether nodes of edges are ordered.
        """
        self.v1.add_related_bidirectional(self.v2)
        self.assertNotEqual(self.v1, self.v2)
        self.assertEqual(self.v1, self.v2.related.pop())

    def test_num_ports(self):
        """
        Tests whether nodes of edges are ordered.
        """
        self.v1.add_related_bidirectional(self.v2)
        with self.assertRaises(AssertionError):
          self.v1.add_related_bidirectional(self.v3)


class GolfGraphTest(BaseTest):
    """
    Tests various graph operations.
    """

    def setUp(self):
        self.order = 32
        self.degree = 4
        self.graph = GolfGraph(self.order, self.degree)

    def test_graph_creation(self):
        """
        Tests if all nodes are created correctly.
        """

        # all initial nodes
        vertices = self.graph.vertices
        degree = self.degree
        for i in range(self.order):
          self.assertIn(Vertex(i, degree), vertices)
