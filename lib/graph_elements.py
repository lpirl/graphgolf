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

        self.breadcrumb = None
        """
        An attribute where non-recursive path finding algorithms can
        store link to find their way back (i.e., to reconstruct the
        path they went but didn't remember).
        """

        self.edges_to = list()
        self.__repr__ = self.__str__

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return "V-%i" % self.id

    def __repr__(self):
        return self.__repr__()

class GolfGraph(object):
    """
    A graph specifically crafted for
    `the graph golf challenge <http://research.nii.ac.jp/graphgolf/>`__.
    """

    def __init__(self, order, degree):
        self.order = order
        self.degree = degree

        # ``list`` because needs fast iteration
        self.vertices = [Vertex(i) for i in range(order)]

    def add_edge_unsafe(self, vertex_a, vertex_b):
        """
        Adds an edge between the two given vertices w/o checking constraints.
        """
        assert vertex_a != vertex_b
        debug("wiring %s and %s", vertex_a, vertex_b)
        vertex_a.edges_to.append(vertex_b)
        vertex_b.edges_to.append(vertex_a)
        assert len(vertex_a.edges_to) <= self.degree
        assert len(vertex_b.edges_to) <= self.degree

    def can_add_edge(self, vertex_a, vertex_b):
        """
        Returns ``True`` if adding an edge between ``vertex_a`` and
        ``vertex_b`` would not violate any constraints.
        """

        # do not make self-edges_to
        if vertex_a == vertex_b:
            debug("constraints check: vertices are actually the same")
            return False

        degree = self.degree
        vertex_a_related = vertex_a.edges_to

        # honor degree at vertex a
        if len(vertex_a_related) == degree:
            debug("constraints check: vertex a has no ports left")
            return False
        assert len(vertex_a_related) < degree

        # honor degree at vertex b
        if len(vertex_b.edges_to) == degree:
            debug("constraints check: vertex b has no ports left")
            return False
        assert len(vertex_b.edges_to) < degree

        # do not add edges_to that already exist
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
        This implementation targets graphs with no initial edges_to.
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

    def shortest_path(self, vertex_a, vertex_b):
        """
        Returns the shortest path from ``vertex_a`` to ``vertex_b``.
        Breadth-First search.
        """

        # ``set`` because needs fast lookup:
        ever_enqueued = {vertex_a}

        # ``list`` because this must be ordered
        # (to not descend accidentally while doing breadth-first search):
        currently_enqueued = [vertex_a]

        # unset breadcrumb at departure vertex that might be left over
        # previous searches
        vertex_a.breadcrumb = None

        # breadth-first walk the graph and lay breadcrumbs until the
        # desired vertex is found
        currently_visiting = None
        while currently_enqueued:
            currently_visiting = currently_enqueued.pop(0)
            if currently_visiting == vertex_b:
                break
            for edge_to in currently_visiting.edges_to:
                if edge_to not in ever_enqueued:
                    edge_to.breadcrumb = currently_visiting
                    ever_enqueued.add(edge_to)
                    currently_enqueued.append(edge_to)

        # follow back the breadcrumbs and remember the path this time
        path = []
        while currently_visiting is not None:
            path.append(currently_visiting)
            currently_visiting = currently_visiting.breadcrumb
        path.reverse()

        return path
