from itertools import permutations

from test import BaseTest
from lib.graph_elements import GolfGraph, Vertex

class GolfGraphTest(BaseTest):
    """
    Tests various graph operations.
    """

    @staticmethod
    def some_graph():
        return GolfGraph(32, 4)

    def test_vertex_creation(self):
        """
        Tests whether all vertices are created correctly.
        """

        graph = self.some_graph()
        vertices = graph.vertices
        degree = graph.degree

        self.assertTrue(len(vertices) == graph.order)
        for i in range(graph.order):
          self.assertIn(Vertex(i), vertices)

    def test_degree_invariant(self):
        """
        Tests whether we cannot add more edges than ``graph.degree``.
        """
        graph = self.some_graph()
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
        graph = self.some_graph()
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
        Asserts shortest path computation for a 'line graph' with 3 vertexes.
        """
        graph = GolfGraph(3, 2)
        vertex0 = graph.vertices[0]
        vertex1 = graph.vertices[1]
        vertex2 = graph.vertices[2]

        # construct
        self.assertTrue(graph.add_edge_pessimist(vertex0, vertex1))
        self.assertTrue(graph.add_edge_pessimist(vertex1, vertex2))

        # check
        self.assertEqual([vertex0, vertex1],
                         graph.shortest_path(vertex0, vertex1))
        self.assertEqual([vertex1, vertex2],
                         graph.shortest_path(vertex1, vertex2))
        self.assertEqual(set((vertex0, vertex1, vertex2)),
                         set(graph.shortest_path(vertex0, vertex2)))

    def test_shortest_path_triangle(self):
        """
        Asserts shortest path computation for a 'triangle graph'.
        """
        graph = GolfGraph(3, 2)
        vertices = graph.vertices
        edges = ((0, 1), (1, 2), (2, 0))

        # construct
        for vertex_a_i, vertex_b_i in edges:
            self.assertTrue(
                graph.add_edge_pessimist(vertices[vertex_a_i],
                                         vertices[vertex_b_i])
                )

        # check
        for vertex_a_i, vertex_b_i in edges:
            edge = [vertices[vertex_a_i], vertices[vertex_b_i]]
            self.assertEqual(edge, graph.shortest_path(*edge))

    def test_average_shortest_path_triangle(self):
        """
        Asserts shortest path computation for a 'triangle graph'.
        """
        graph = GolfGraph(3, 2)
        vertices = graph.vertices
        edges = ((0, 1), (1, 2), (2, 0))

        # construct
        for vertex_a_i, vertex_b_i in edges:
            self.assertTrue(
                graph.add_edge_pessimist(vertices[vertex_a_i],
                                         vertices[vertex_b_i])
                )

        self.assertEqual(graph.average_shortes_path_length(), 1)

    def test_average_shortest_path_rectangle(self):
        """
        Asserts shortest path computation for a 'triangle graph'.
        """
        graph = GolfGraph(4, 2)
        vertices = graph.vertices
        edges = ((0, 1), (1, 2), (2, 3), (3, 0))

        # construct
        for vertex_a_i, vertex_b_i in edges:
            self.assertTrue(
                graph.add_edge_pessimist(vertices[vertex_a_i],
                                         vertices[vertex_b_i])
                )

        self.assertEqual(graph.average_shortes_path_length(), 4/3)
