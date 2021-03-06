"""
Tests various operations of graph elements.
"""

from itertools import permutations, combinations
from copy import deepcopy
from pickle import loads, dumps

from test import BaseTest
from lib.graph_elements import GolfGraph, Vertex, GraphPartitionedError

class GolfGraphTest(BaseTest):
    """
    See module docstring.
    """

    @staticmethod
    def unconnected_graph():
        """
        Returns a unconnected graph (that, according to its configuration,
        could have edges, however).
        """
        return GolfGraph(32, 4)

    @staticmethod
    def line_graph():
        """
        Returns a graph with two vertices connected.
        """
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
        """
        Returns a graph with three vertices, connected as a "circle"
        (think: triangle).
        """
        graph = GolfGraph(3, 2)
        vertices = graph.vertices
        edges = ((0, 1), (1, 2), (2, 0))

        # construct
        for vertex_a_i, vertex_b_i in edges:
            graph.add_edge_unsafe(vertices[vertex_a_i], vertices[vertex_b_i])

        return graph

    @staticmethod
    def rectangle_graph():
        """
        Returns a graph with four vertices, connected as a "circle"
        (think: rectangle).
        """
        graph = GolfGraph(4, 2)
        vertices = graph.vertices
        edges = ((0, 1), (1, 2), (2, 3), (3, 0))

        # construct
        for vertex_a_i, vertex_b_i in edges:
            graph.add_edge_unsafe(vertices[vertex_a_i], vertices[vertex_b_i])

        return graph

    @staticmethod
    def some_valid_graphs():
        """
        Returns a bunch of graphs with valid combinations of order and
        degree.
        """
        orders = (3, 4, 32, 33)
        degrees = (2, 3, 4, 32, 33)
        for order in orders:
            for degree in degrees:
                graph = GolfGraph(order, degree)
                graph.add_as_many_random_edges_as_possible()
                yield graph

    def test_vertex_creation(self):
        """
        Tests whether all vertices are created correctly.
        """

        graph = self.unconnected_graph()
        vertices = graph.vertices
        degree = graph.degree

        self.assertTrue(len(vertices) == graph.order)
        ids = set(v.id for v in graph.vertices)
        for i in range(graph.order):
          self.assertIn(i, ids)

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
        for graph in self.some_valid_graphs():
            vertices_with_unused_ports = set()
            for vertex in graph.vertices:
                edges_to = vertex.edges_to

                # no more edges_to vertices than the degree allows for
                self.assertTrue(len(edges_to) <= graph.degree)

                # not fewer connections than allowed (if applicable)
                if len(edges_to) < graph.degree:
                    vertices_with_unused_ports.add(vertex)

                # no self-connections
                self.assertNotIn(vertex, edges_to)

                # no duplicates in edges_to vertices
                self.assertEqual(len(edges_to), len(set(edges_to)))

            if (graph.order - 1) == graph.degree:
                self.assertTrue(len(vertices_with_unused_ports) < 2)

    def test_hops_two_vertices(self):
        """
        Tests shortest path computation for graph with two vertices.
        """
        graph = GolfGraph(2, 2)
        graph.add_as_many_random_edges_as_possible()
        graph.analyze()
        self.assertEqual(tuple(), graph.hops(*graph.vertices))

    def test_hops_line(self):
        """
        Tests shortest path computation for a 'line graph' with 3 vertices.
        """
        graph = self.line_graph()
        graph.analyze()
        vertices = graph.vertices
        self.assertEqual(tuple(), graph.hops(vertices[0], vertices[1]))
        self.assertEqual(tuple(), graph.hops(vertices[1], vertices[2]))
        self.assertEqual((vertices[1], ),
                         graph.hops(vertices[0], vertices[2]))

    def test_hops_triangle(self):
        """
        Tests shortest path computation for a 'triangle graph'.
        """
        graph = self.triangle_graph()
        graph.analyze()

        for edge in permutations(graph.vertices, 2):
            self.assertEqual(tuple(), tuple(graph.hops(*edge)))

    def test_hops_fully_connected(self):
        """
        Tests shortest path computation for some fully connected graphs.
        """
        orders_degrees = ((5, 4), (10, 9), (10, 11))
        for order, degree in orders_degrees:
            graph = GolfGraph(order, degree)
            graph.add_as_many_random_edges_as_possible()
            graph.analyze()
            self.assertEqual(1, graph.diameter)
            self.assertEqual(1, graph.aspl)

    def test_analyze_unconnected(self):
        """
        Checks analysis results for an unconnected graph.
        """
        graph = GolfGraph(3, 2)

        with self.assertRaises(GraphPartitionedError):
            graph.analyze()

    def test_analyze_triangle(self):
        """
        Checks analysis results for a 'triangle graph'.
        """
        graph = self.triangle_graph()

        graph.analyze()
        self.assertEqual(graph.diameter, 1)
        self.assertEqual(graph.aspl, 1)

    def test_analyze_rectangle(self):
        """
        Checks analysis results for a 'triangle graph'.
        """
        graph = self.rectangle_graph()

        graph.analyze()
        self.assertEqual(graph.diameter, 2)
        self.assertEqual(graph.aspl, 4/3)

    def test_remove_edge(self):
        """
        Tests whether removing and edge makes the path longer
        (for the 'line graph').
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
        Tests whether removing and edge makes the path longer
        (for the 'rectangle graph').
        """
        graph = self.rectangle_graph()
        vertices = graph.vertices
        graph.remove_edge_unsafe(vertices[0], vertices[-1])
        graph.analyze()
        self.assertEqual(tuple(vertices[1:-1]),
                         graph.hops(vertices[0], vertices[-1]))

    def test_duplicate_rectangle(self):
        """
        Tests graph duplication.
        """
        graph_a = self.rectangle_graph()
        graph_a.analyze()
        graph_b = graph_a.duplicate()

        vertex_a0, vertex_a1 = graph_a.vertices[0:2]
        vertex_b0, vertex_b1 = graph_b.vertices[0:2]

        # check that the hops caches do not point to the old graph's
        # vertices
        for vertex_a, vertex_b in combinations(graph_a.vertices, 2):
            hops_a = graph_a.hops_cache.get(vertex_a, vertex_b)
            hops_b = graph_b.hops_cache.get(vertex_a, vertex_b)
            for hop_a, hop_b in zip(hops_a, hops_b):
                self.assertNotEqual(id(hop_a), id(hop_b))

        # modify graph a
        graph_a.remove_edge_unsafe(vertex_a0, vertex_a1)

        # assert graph b not modified
        self.assertIn(vertex_b1, vertex_b0.edges_to)
        self.assertIn(vertex_b0, vertex_b1.edges_to)

    def test_edges_rectangle(self):
        """
        Tests whether ``edges()`` does what we expect.
        """
        graph = self.rectangle_graph()
        edges = graph.edges()

        self.assertEqual(4, len(edges))
        self.assertIn((graph.vertices[1], graph.vertices[2]), edges)
        self.assertNotIn((graph.vertices[0], graph.vertices[2]), edges)

    def test_ideal_true(self):
        """
        Tests whether ``ideal()`` does what we expect.
        """
        # the function ``lower_bounds`` is quite crappy and does not
        # calculate correct values for edge cases. A "rectangle graph"
        # is the smallest graph supported.

        graph = self.rectangle_graph()
        graph.analyze()
        self.assertTrue(graph.ideal())
        graph.remove_edge_unsafe(graph.vertices[1], graph.vertices[2])
        graph.analyze()
        self.assertFalse(graph.ideal())

    def test_no_duplicate_vertices(self):
        """
        Tests whether we can have equal but non-identical vertices.
        We shouldn't, since - in our specific case - it would suggest
        duplicate vertices in memory and hence, inefficiency.
        """
        with self.assertRaises(AssertionError):
            Vertex(1) == Vertex(1)

    def test_pickle_and_unpickle(self):
        """
        Tests graph pickling.
        """
        for graph in self.some_valid_graphs():
            graph.analyze()
            unpickled = loads(dumps(graph))

            # two times: 1st as unpickled, 2nd re-analyzed
            for _ in range(2):

                for attr_name in ("order", "degree", "aspl", "diameter"):
                    self.assertEqual(
                        getattr(graph, attr_name),
                        getattr(unpickled, attr_name),
                    )

                for edge_a, edge_b in zip(graph.edges(), unpickled.edges()):

                    # we cannot compare the vertices directly (would raise
                    # assertions) so we iterate over eeeeverything...

                    # compare edges themselves
                    self.assertEqual(
                        tuple(v.id for v in edge_a),
                        tuple(v.id for v in edge_b)
                    )

                    # compare hops caches
                    for vertex_a, vertex_b in combinations(graph.vertices, 2):
                        hops_a = graph.hops_cache.get(vertex_a, vertex_b)
                        hops_b = unpickled.hops_cache.get(vertex_a, vertex_b)
                        for hop_a, hop_b in zip(hops_a, hops_b):
                            self.assertEqual(hop_a.id, hop_b.id)

                    self.assertEqual(graph.diameter, unpickled.diameter)
                    self.assertEqual(graph.aspl, unpickled.aspl)
                    self.assertEqual(graph.mspl, unpickled.mspl)

    def test_hops_cache_reverse_lookup(self):
        """
        Tests absence of a wrong ASPL that was returned for a specific
        graph after implementing reverse hops cache lookups.
        """
        graph = GolfGraph(32, 5)
        edges = [
            (0, [2, 31, 8, 16, 15]),
            (1, [4, 26, 27, 29, 11]),
            (2, [25, 29, 15, 7]),
            (3, [18, 17, 27, 8, 16]),
            (4, [21, 5, 28, 10]),
            (5, [14, 22, 24, 15]),
            (6, [16, 14, 30, 19, 9]),
            (7, [13]),
            (7, [20, 12, 10]),
            (8, [29, 15, 24]),
            (9, [23, 18, 28, 22]),
            (10, [24, 16, 11]),
            (11, [22, 26, 17]),
            (12, [31, 30, 14, 29]),
            (13, [17, 28, 19, 23]),
            (14, [21, 25]),
            (15, [23]),
            (16, [20]),
            (17, [22, 26]),
            (18, [29, 26, 24]),
            (19, [22, 27, 20]),
            (20, [25, 23]),
            (21, [30, 25, 23]),
            (24, [31]),
            (25, [26]),
            (27, [31, 28]),
            (28, [30]),
            (30, [31]),
            ]
        for vertex_a_i, vertex_b_is in edges:
            for vertex_b_i in vertex_b_is:
                graph.add_edge_unsafe(
                    graph.vertices[vertex_a_i],
                    graph.vertices[vertex_b_i]
                )
        graph.analyze()
        self.assertEqual(graph.diameter, 4)
        self.assertEqual(round(graph.aspl, 12), 2.20564516129)

    def test_comparison(self):
        """
        Tests whether our implementation of ``__lt__`` does what we want.
        """
        orders_degrees = ((5, 4), (10, 9), (10, 11))
        for order, degree in orders_degrees:
            graph_a = GolfGraph(order, degree)
            graph_a.add_as_many_random_edges_as_possible()
            graph_a.analyze()
            graph_b = graph_a.duplicate()
            self.assertFalse(graph_a < graph_b)
            self.assertFalse(graph_a > graph_b)
            graph_b.remove_edge_unsafe(graph_b.vertices[0],
                                       graph_b.vertices[1])
            graph_b.analyze()
            self.assertTrue(graph_a < graph_b)
