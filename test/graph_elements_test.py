from test import BaseTest

from lib.graph_elements import GolfGraph, Vertex

#~ class VertexTest(BaseTest):
    #~ """
    #~ Tests class ``Vertex``.
    #~ """

    #~ def setUp(self):
        #~ self.v1 = Vertex(1)
        #~ self.v2 = Vertex(2)
        #~ self.v3 = Vertex(3)

    #~ def test_order(self):
        #~ """
        #~ Tests whether nodes of edges are ordered.
        #~ """
        #~ self.v1.add_edge(self.v2)
        #~ self.assertNotEqual(self.v1, self.v2)
        #~ self.assertEqual(self.v1, self.v2.related.pop())

    #~ def test_num_ports(self):
        #~ """
        #~ Tests whether nodes of edges are ordered.
        #~ """
        #~ self.v1.add_edge(self.v2)
        #~ with self.assertRaises(AssertionError):
          #~ self.gra.v1.add_edge(self.v3)


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
        Tests whether all vertices are created correctly.
        """

        # all initial nodes
        vertices = self.graph.vertices
        degree = self.degree
        for i in range(self.order):
          self.assertIn(Vertex(i), vertices)

    def test_degree_invariant(self):
        """
        Tests whether we cannot add more edges than ``self.degree``.
        """
        graph = self.graph
        vertices = graph.vertices
        add_edge = graph.add_edge
        vertex_to_add_to = vertices[-1]

        assert len(vertices) > self.degree

        # do what is allowed
        for i in range(self.degree):
          add_edge(vertex_to_add_to, vertices[i])

        with self.assertRaises(AssertionError):
          add_edge(vertex_to_add_to, vertices[-2])

    def test_no_self_edges(self):
        """
        Tests whether we cannot add an edges between a vertex and itself.
        """
        vertex = self.graph.vertices[0]
        with self.assertRaises(AssertionError):
          self.graph.add_edge(vertex, vertex)
