from itertools import permutations
from copy import deepcopy

from test import BaseTest
from lib.graph_elements import GolfGraph, Vertex

class GolfGraphTest(BaseTest):
    """
    Tests various graph operations.
    """

    @staticmethod
    def unconnected_graph():
        return GolfGraph(32, 4)

    @staticmethod
    def line_graph():
        graph = GolfGraph(3, 2)
        vertex0 = graph.vertices[0]
        vertex1 = graph.vertices[1]
        vertex2 = graph.vertices[2]

        # construct
        graph.add_edge_unsafe(vertex0, vertex1)
        graph.add_edge_unsafe(vertex1, vertex2)

        return graph

    @staticmethod
    def triangle_graph():
        graph = GolfGraph(3, 2)
        vertices = graph.vertices
        edges = ((0, 1), (1, 2), (2, 0))

        # construct
        for vertex_a_i, vertex_b_i in edges:
            graph.add_edge_unsafe(vertices[vertex_a_i], vertices[vertex_b_i])

        return graph

    @staticmethod
    def rectangle_graph():
        graph = GolfGraph(4, 2)
        vertices = graph.vertices
        edges = ((0, 1), (1, 2), (2, 3), (3, 0))

        # construct
        for vertex_a_i, vertex_b_i in edges:
            graph.add_edge_unsafe(vertices[vertex_a_i], vertices[vertex_b_i])

        return graph

    def test_vertex_creation(self):
        """
        Tests whether all vertices are created correctly.
        """

        graph = self.unconnected_graph()
        vertices = graph.vertices
        degree = graph.degree

        self.assertTrue(len(vertices) == graph.order)
        for i in range(graph.order):
          self.assertIn(Vertex(i), vertices)

    def test_degree_invariant(self):
        """
        Tests whether we cannot add more edges than ``graph.degree``.
        """
        graph = self.unconnected_graph()
        vertices = graph.vertices
        add_edge_unsafe = graph.add_edge_unsafe
        vertex_to_add_to = vertices[-1]

        assert len(vertices) > graph.degree

        # do what is allowed
        for i in range(graph.degree):
            add_edge_unsafe(vertex_to_add_to, vertices[i])

        with self.assertRaises(AssertionError):
            add_edge_unsafe(vertex_to_add_to, vertices[-2])

    def test_no_self_edges(self):
        """
        Tests whether we cannot add an edges between a vertex and itself.
        """
        graph = self.unconnected_graph()
        vertex = graph.vertices[0]
        with self.assertRaises(AssertionError):
            graph.add_edge_unsafe(vertex, vertex)

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
                edges_to = vertex.edges_to

                # no more edges_to vertices than the degree allows for
                if degree >= 0:
                    self.assertTrue(len(edges_to) <= degree)

                # no self-connections
                self.assertNotIn(vertex, edges_to)

                # no duplicates in edges_to vertices
                self.assertEqual(len(edges_to), len(set(edges_to)))

    def test_shortest_path_one_vertex(self):
        """
        Asserts shortest path computation for graph with one vertex.
        """
        graph = GolfGraph(1, 1)
        graph.add_as_many_random_edges_as_possible()
        vertex = graph.vertices[0]
        self.assertEqual(graph.vertices,
                         graph.shortest_path(vertex, vertex))

    def test_shortest_path_two_vertices(self):
        """
        Asserts shortest path computation for graph with two vertices.
        """
        graph = GolfGraph(2, 1)
        graph.add_as_many_random_edges_as_possible()
        self.assertEqual(graph.vertices,
                         graph.shortest_path(*graph.vertices))

    def test_shortest_path_line(self):
        """
        Asserts shortest path computation for a 'line graph' with 3 vertices.
        """
        graph = self.line_graph()
        vertices = graph.vertices
        self.assertEqual([vertices[0], vertices[1]],
                         graph.shortest_path(vertices[0], vertices[1]))
        self.assertEqual([vertices[1], vertices[2]],
                         graph.shortest_path(vertices[1], vertices[2]))
        self.assertEqual([vertices[0], vertices[1], vertices[2]],
                         graph.shortest_path(vertices[0], vertices[2]))

    def test_shortest_path_triangle(self):
        """
        Asserts shortest path computation for a 'triangle graph'.
        """
        graph = self.triangle_graph()

        for edge in permutations(graph.vertices, 2):
            self.assertEqual(list(edge), graph.shortest_path(*edge))

    def test_shortest_path_fully_connected(self):
        """
        Asserts shortest path computation for some fully connected graphs.
        """
        orders_degrees = ((5, 4), (10, 9), (10, 11))
        for order, degree in orders_degrees:
            graph = GolfGraph(order, degree)
            graph.add_as_many_random_edges_as_possible()
            graph.analyze()
            self.assertEqual(1, graph.diameter)
            self.assertEqual(1, graph.average_shortest_path_length)

    def test_analyze_unconnected(self):
        """
        Checks analysis results for an unconnected graph.
        """
        graph = GolfGraph(3, 2)

        with self.assertRaises(AssertionError):
            graph.analyze()

    def test_analyze_triangle(self):
        """
        Checks analysis results for a 'triangle graph'.
        """
        graph = self.triangle_graph()

        graph.analyze()
        self.assertEqual(graph.diameter, 1)
        self.assertEqual(graph.average_shortest_path_length, 1)

    def test_analyze_rectangle(self):
        """
        Checks analysis results for a 'triangle graph'.
        """
        graph = self.rectangle_graph()

        graph.analyze()
        self.assertEqual(graph.diameter, 2)
        self.assertEqual(graph.average_shortest_path_length, 4/3)

    def test_remove_edge(self):
        """
        Tests whether removing and edge makes the path longer.
        """
        graph = self.line_graph()
        vertices = graph.vertices
        vertex0 = vertices[0]
        vertex1 = vertices[1]
        vertex2 = vertices[2]

        # this is what we expect from the test code
        assert vertex1 in vertex0.edges_to
        assert vertex2 in vertex1.edges_to

        graph.remove_edge_unsafe(vertex0, vertex1)

        # this is what we expect from the actual code
        self.assertNotIn(vertex1, vertex0.edges_to)
        self.assertIn(vertex2, vertex1.edges_to)

    def test_remove_edge_rectangle(self):
        """
        Tests whether removing and edge makes the path longer.
        """
        graph = self.rectangle_graph()
        vertices = graph.vertices
        graph.remove_edge_unsafe(vertices[0], vertices[-1])
        self.assertEqual(vertices,
                         graph.shortest_path(vertices[0], vertices[-1]))

    def test_duplicate_rectangle(self):
        """
        Tests graph duplication.
        """
        graph_a = self.rectangle_graph()
        graph_b = graph_a.duplicate()

        graph_a.remove_edge_unsafe(graph_a.vertices[0], graph_a.vertices[1])
        self.assertIn(graph_b.vertices[1], graph_b.vertices[0].edges_to)
        self.assertIn(graph_b.vertices[0], graph_b.vertices[1].edges_to)

    def test_edges_rectangle(self):
        """
        Tests whether ``edges()`` does what we expect.
        """
        graph = self.rectangle_graph()
        edges = graph.edges()

        self.assertEqual(4, len(edges))
        self.assertIn((graph.vertices[1], graph.vertices[2]), edges)
        self.assertNotIn((graph.vertices[0], graph.vertices[2]), edges)
