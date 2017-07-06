"""
All elements of a graph.
"""

from logging import debug, info
from random import shuffle
from itertools import permutations



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
        info("initializing graph")
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

    def add_as_many_random_edges_as_possible(self):
        """
        Adds random edges to the graph, to the maximum what
         ``self.degree`` allows.
        This implementation targets graphs with no initial edges_to.

        For optimization purposes, this is an terrible all-in-one function.
        """
        info("connecting graph randomly")

        degree = self.degree
        vertices_with_ports_left = list(self.vertices)

        # repeat ``degree`` times
        for _ in range(degree):

            if len(vertices_with_ports_left) < 2:
                break

            current_vertices = list(vertices_with_ports_left)
            shuffle(current_vertices)

            # repeat until no(t enough) vertices left
            while len(current_vertices) > 1:

                vertex_a = current_vertices.pop(0)
                debug("searching random connection for %s", vertex_a)

                # honor degree at vertex a
                if len(vertex_a.edges_to) == degree:
                    debug("vertex a has no ports left")
                    vertices_with_ports_left.remove(vertex_a)
                    continue
                assert len(vertex_a.edges_to) < degree

                # search for a vertex to connect to
                for vertex_b in current_vertices:

                    # honor degree at vertex b
                    if len(vertex_b.edges_to) == degree:
                        debug("vertex b has no ports left")
                        continue
                    assert len(vertex_b.edges_to) < degree

                    # do not add edges_to that already exist
                    if vertex_b in vertex_a.edges_to:
                        debug("vertices already connected")
                        continue

                    # do not add self-edges
                    if vertex_a == vertex_b:
                        debug("vertices are the same")
                        continue

                    # no constraints violated, let's connect to this vertex
                    current_vertices.remove(vertex_b)
                    self.add_edge_unsafe(vertex_a, vertex_b)
                    break

    def shortest_path(self, vertex_a, vertex_b):
        """
        Returns the shortest path from ``vertex_a`` to ``vertex_b``.
        Breadth-First search.
        """
        info("searching shortest path between %s and %s", vertex_a,
             vertex_b)

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

    def shortest_path_length(self, vertex_a, vertex_b):
        """
        Returns the shortest path length from ``vertex_a`` to ``vertex_b``.
        """
        return len(self.shortest_path(vertex_a, vertex_b)) - 1

    def analzye(self):
        """
        Returns the (average shortest path length, diameter) of the graph.
        """
        info("analyzing graph")
        if not self.vertices:
            raise RuntimeError(
                "Don't know how to analyze an empty graph."
            )
        longest_shortest_path = -1
        lengths_sum = 0
        count = 0
        for vertex_a, vertex_b in permutations(self.vertices, 2):
            length = self.shortest_path_length(vertex_a, vertex_b)
            longest_shortest_path = max(longest_shortest_path, length)
            lengths_sum += length
            count += 1
        return (lengths_sum/count, longest_shortest_path)
