from itertools import permutations

from test import BaseTest
from lib.graph_elements import GolfGraph, Vertex

class GolfGraphTest(BaseTest):
    """
    Tests various graph operations.
    """

    def setUp(self):
        self.order = 32
        self.degree = 4
        self.graph = GolfGraph(self.order, self.degree)

    def test_vertex_creation(self):
        """
        Tests whether all vertices are created correctly.
        """

        vertices = self.graph.vertices
        degree = self.degree

        self.assertTrue(len(vertices) == self.graph.order)
        for i in range(self.order):
          self.assertIn(Vertex(i), vertices)

    def test_degree_invariant(self):
        """
        Tests whether we cannot add more edges than ``self.degree``.
        """
        graph = self.graph
        vertices = graph.vertices
        add_edge_unsafe = graph.add_edge_unsafe
        vertex_to_add_to = vertices[-1]

        assert len(vertices) > self.degree

        # do what is allowed
        for i in range(self.degree):
            add_edge_unsafe(vertex_to_add_to, vertices[i])

        with self.assertRaises(AssertionError):
            add_edge_unsafe(vertex_to_add_to, vertices[-2])

    def test_no_self_edges(self):
        """
        Tests whether we cannot add an edges between a vertex and itself.
        """
        vertex = self.graph.vertices[0]
        with self.assertRaises(AssertionError):
            self.graph.add_edge_unsafe(vertex, vertex)

    def test_add_as_many_random_edges_as_possible(self):
        """
        Tests random vertex connections for a whole bunch of graphs with
        common but also weird combinations of order and degree.
        """

        # some common cases: negative, zero, odd, even, small, big
        values = (-1, 0, 1, 3, 4, 32, 33)
        test_cases = permutations(values, 2)

        for order, degree in test_cases:
            graph = GolfGraph(order, degree)
            graph.add_as_many_random_edges_as_possible()
            for vertex in graph.vertices:
                related = vertex.related

                # no more related vertices than the degree allows for
                if degree >= 0:
                    self.assertTrue(len(related) <= degree)

                # no self-connections
                self.assertNotIn(vertex, related)

                # no duplicates in related vertices
                self.assertEqual(len(related), len(set(related)))
