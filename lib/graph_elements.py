"""
All elements of a graph.
"""

from logging import debug
from random import shuffle



class Vertex(object):
    """
    A node in a graph.
    Keep this minimal.
    """

    def __init__(self, id):
        self.id = id
        self.related = list()
        self.__repr__ = self.__str__

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return "V-%i" % self.id

    def __str__(self):
        return self.__repr__()

class GolfGraph(object):
    """
    A graph specifically crafted for
    `the graph golf challenge <http://research.nii.ac.jp/graphgolf/>`__.
    """

    def __init__(self, order, degree):
        self.order = order
        self.degree = degree

        self.vertices = [Vertex(i) for i in range(order)]

    def add_edge_unsafe(self, vertex_a, vertex_b):
        """
        Adds an edge between the two given vertices w/o checking constraints.
        """
        assert vertex_a != vertex_b
        debug("wiring %s and %s", vertex_a, vertex_b)
        vertex_a.related.append(vertex_b)
        vertex_b.related.append(vertex_a)
        assert len(vertex_a.related) <= self.degree
        assert len(vertex_b.related) <= self.degree

    def can_add_edge(self, vertex_a, vertex_b):
        """
        Returns ``True`` if adding an edge between ``vertex_a`` and
        ``vertex_b`` would not violate any constraints.
        """

        # do not make self-connections
        if vertex_a == vertex_b:
            debug("constraints check: vertices are actually the same")
            return False

        degree = self.degree
        vertex_a_related = vertex_a.related

        # honor degree at vertex a
        if len(vertex_a_related) == degree:
            debug("constraints check: vertex a has no ports left")
            return False
        assert len(vertex_a_related) < degree

        # honor degree at vertex b
        if len(vertex_b.related) == degree:
            debug("constraints check: vertex b has no ports left")
            return False
        assert len(vertex_b.related) < degree

        # do not add connections that already exist
        if vertex_b in vertex_a_related:
            debug("constraints check: vertices already connected")
            return False

        return True

    def add_edge_pessimist(self, vertex_a, vertex_b):
        """
        Adds an edge between the two given vertices if constraints are
        not violated. Returns success as Boolean value.
        """
        if self.can_add_edge(vertex_a, vertex_b):
            self.add_edge_unsafe(vertex_a, vertex_b)
            return True
        return False

    def add_as_many_random_edges_as_possible(self):
        """
        Adds random edges to the graph, to the maximum what
         ``self.degree`` allows.
        This implementation targets graphs with no initial connections.
        """

        def connect_vertex(vertex_a, vertices_b):
            """
            Connects ``vertex`` to any of ``vertices`` and returns the
            index in ``vertices`` that ``vertex`` has been connected to,
            ``None`` otherwise
            """
            debug("searching random connection for %s", vertex_a)
            vertex_b_i = 0
            len_vertices = len(vertices)

            while not add_edge_pessimist(vertex_a, vertices_b[vertex_b_i]):
                vertex_b_i += 1
                if vertex_b_i >= len_vertices:
                    return None
            return vertex_b_i

        add_edge_pessimist = self.add_edge_pessimist

        # repeat ``degree`` times
        for _ in range(self.degree):

            vertices = list(self.vertices)
            shuffle(vertices)

            # repeat until no(t enough) vertices left
            while len(vertices) > 1:
                i_connected_to = connect_vertex(vertices.pop(0),
                                                       vertices)
                if i_connected_to:
                    vertices.pop(i_connected_to)
