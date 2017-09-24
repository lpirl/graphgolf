"""
Tests enhancer operations.
"""

from itertools import combinations

from test import BaseTest
from lib.graph_elements import GolfGraph, Vertex, GraphPartitionedError
from lib.enhancers import Registry



class GolfGraphTest(BaseTest):
    """
    See module docstring.
    """

    def assert_all_edges_used(self, graph):
        """
        Tests whether there are as many edges as allowed connected to all
        vertices.
        """
        vertices_with_ports_left = [v for v in graph.vertices
                                    if len(v.edges_to) < graph.degree]

        # now, with all the vertices that have less than degree edges,
        # we assert that they are already connected and no more edge can
        # be added
        for vertex_a, vertex_b in combinations(vertices_with_ports_left, 2):
            self.assertIn(vertex_a, vertex_b.edges_to)

    def test_all_edges(self):
        """
        Tests whether there are as many edges as allowed (i.e. degree)
        after an modification.
        """
        original = GolfGraph(10, 3)
        original.add_as_many_random_edges_as_possible()
        original.analyze()
        self.assert_all_edges_used(original)
        for Enhancer in Registry.enhancers:
            enhancer = Enhancer(None)
            while True:
                try:
                    modified = enhancer.modify_graph(original.duplicate())
                except GraphPartitionedError:
                    continue
                else:
                    break
            self.assert_all_edges_used(modified)
