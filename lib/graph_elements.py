"""
All elements of a graph.
"""

from logging import debug, warning
from random import shuffle
from itertools import combinations
from math import ceil



class Vertex(object):
    """
    A node in a graph.

    We keep this minimal since we'll have a lot of vertices in memory.
    Therefore, most logic is implemented in ``GolfGraph``.
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
        """
        The main data structure to represent edges.
        This list contains vertices this vertex has edges to.
        Accordingly, this vertex can be found in ``edges_to`` of the
        vertices in ``edges_to`` (think: bidirectionally linked).
        """

        self.shortest_path_cache = dict()
        """
        A cache for found paths.
        Maps target vertices to shortest paths.
        """

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        """
        Ordering vertices can be useful for optimizations
        (e.g, avoid the use of sets by always creating edges with
        the "smaller" vertex first).
        """
        return self.id < other.id

    def __str__(self):
        return "V-%i" % self.id

    def __repr__(self):
        return self.__str__()

class GolfGraph(object):
    """
    A graph specifically crafted for
    `the graph golf challenge <http://research.nii.ac.jp/graphgolf/>`__.
    """

    def __init__(self, order, degree):
        debug("initializing graph")

        assert order > -1
        assert degree > -1

        self.order = order
        self.degree = degree

        self._aspl_lower_bound = None
        self._diameter_lower_bound = None

        # to be filled by ``self.analyze()``
        self.diameter = None
        self.aspl = None

        # ``list`` because needs fast iteration
        self.vertices = [Vertex(i) for i in range(order)]

        self.modified_vertices = set()
        """
        In this set, we can collect modified vertices, for which we
        have to invalidate the shortest path caches later on.
        That way, we can invalidate the caches all at once instead of
        upon every modification of edges.
        """

    def __str__(self):
        bits = [
            self.__class__.__name__, str(hex(id(self))),
            "ASPL=%s" % self.aspl or "n/a",
            "diameter=%s" % self.diameter or "n/a",
        ]
        return " ".join(bits)


    def _calculate_lower_bounds(self):
        """
        Returns the lower bound of the (diameter, average shortest path
        length) for the given ``order`` and ``degree``.

        Copied from http://research.nii.ac.jp/graphgolf/py/create-random.py
        """

        assert (self._aspl_lower_bound is None and
                self._diameter_lower_bound is None,
                "lower bounds already calculated")

        order = self.order
        degree = self.degree

        if order < 2:
            warning("could not calculate lower bound for order %i"
                    " (not implemented for order<2)", order)
            return None, None

        if degree < 2:
            warning("could not calculate lower bound for degree %i"
                    " (not implemented for degree<2)", degree)
            return None, None

        diameter = -1
        aspl = 0.0
        n = 1
        r = 1
        while True:
            tmp = n + degree * pow(degree - 1, r - 1)
            if tmp >= order:
                break
            n = tmp
            aspl += r * degree * pow(degree - 1, r - 1)
            diameter = r
            r += 1
        diameter += 1
        aspl += diameter * (order - n)
        aspl /= (order - 1)

        self._aspl_lower_bound = aspl
        self._diameter_lower_bound = diameter

    @property
    def aspl_lower_bound(self):
        """
        Returns the lower bound for the average shortest path length for
        this graph.
        Be aware, that for low values of ``order`` and ``degree``, this
        might return ``None``, due to a lack of implementation.
        """
        if not self._aspl_lower_bound:
            self._calculate_lower_bounds()
        return self._aspl_lower_bound

    @property
    def diameter_lower_bound(self):
        """
        Returns the lower bound for the diameter for this graph.
        Be aware, that for low values of ``order`` and ``degree``, this
        might return ``None``, due to a lack of implementation.
        """
        if not self._diameter_lower_bound:
            self._calculate_lower_bounds()
        return self._diameter_lower_bound

    def add_edge_unsafe(self, vertex_a, vertex_b):
        """
        Adds an edge between the two given vertices w/o checking constraints.

        Called very often, keep minimal.
        """
        assert vertex_a in self.vertices
        assert vertex_b in self.vertices
        assert vertex_a != vertex_b
        debug("wiring %s and %s", vertex_a, vertex_b)
        vertex_a.edges_to.append(vertex_b)
        vertex_b.edges_to.append(vertex_a)
        assert len(vertex_a.edges_to) <= self.degree
        assert len(vertex_b.edges_to) <= self.degree

    def remove_edge_unsafe(self, vertex_a, vertex_b):
        """
        Removes an edge between the two given vertices w/o checking anything.

        Called very often, keep minimal.
        """
        debug("de-wiring %s and %s", vertex_a, vertex_b)
        assert vertex_a in self.vertices
        assert vertex_b in self.vertices
        assert vertex_a != vertex_b, "vertex should not have edge to itself"
        vertex_a.edges_to.remove(vertex_b)
        vertex_b.edges_to.remove(vertex_a)

    def add_as_many_random_edges_as_possible(self, limit_to_vertices=None):
        """
        Adds random edges to the graph, to the maximum what
         ``self.degree`` allows.
        This implementation targets graphs with no initial edges_to.

        For optimization purposes, this is an terrible all-in-one method.
        """
        debug("connecting graph randomly")

        degree = self.degree
        overall_vertices = limit_to_vertices or list(self.vertices)

        # repeat ``degree`` times
        for _ in range(degree):

            if len(overall_vertices) < 2:
                break

            current_vertices = list(overall_vertices)
            shuffle(current_vertices)

            # repeat until no(t enough) vertices left
            while len(current_vertices) > 1:

                vertex_a = current_vertices.pop(0)
                debug("searching random connection for %s", vertex_a)

                # honor degree at vertex a
                if len(vertex_a.edges_to) == degree:
                    debug("vertex a has no ports left")
                    try:
                        # the vertex might be removed already, if it was
                        # found as a "vertex_b" with no ports left
                        overall_vertices.remove(vertex_a)
                    except ValueError:
                        pass
                    continue
                assert len(vertex_a.edges_to) < degree

                # search for a vertex to connect to
                for vertex_b in current_vertices:

                    # honor degree at vertex b
                    if len(vertex_b.edges_to) == degree:
                        debug("vertex b has no ports left")
                        # discouraged
                        current_vertices.remove(vertex_b)
                        overall_vertices.remove(vertex_b)
                        continue
                    assert len(vertex_b.edges_to) < degree

                    # do not add self-edges
                    if vertex_a == vertex_b:
                        debug("vertices are the same")
                        continue

                    # do not add edges_to that already exist
                    if vertex_b in vertex_a.edges_to:
                        debug("vertices already connected")
                        continue

                    # no constraints violated, let's connect to this vertex
                    self.add_edge_unsafe(vertex_a, vertex_b)
                    break

    def shortest_path(self, vertex_a, vertex_b):
        """
        Returns the shortest path from ``vertex_a`` to ``vertex_b``.
        Breadth-First search.

        Called very often, keep efficient.
        """
        debug("searching shortest path between %s and %s", vertex_a,
              vertex_b)

        assert len(self.modified_vertices) == 0

        # this is where we'll store the shortest path in
        # (excluding the departure, but including the destination vertex)
        path = []

        # ``set`` because needs fast lookup:
        ever_enqueued = {vertex_a}

        # ``list`` because this must be ordered
        # (to not descend accidentally while doing breadth-first search):
        currently_enqueued = [vertex_a]

        # unset breadcrumb at departure vertex (it might be not ``None``
        # from previous searches)
        vertex_a.breadcrumb = None

        # non-recursive breadth-first walk the graph and lay breadcrumbs
        # until the desired vertex is found
        currently_visiting = None
        while currently_enqueued:
            currently_visiting = currently_enqueued.pop(0)

            # check if we arrived at the target vertex
            if currently_visiting == vertex_b:
                break

            for edge_to in currently_visiting.edges_to:
                if edge_to not in ever_enqueued:
                    edge_to.breadcrumb = currently_visiting
                    ever_enqueued.add(edge_to)
                    currently_enqueued.append(edge_to)

        # follow back the breadcrumbs and remember the path this time
        # along the way, fill caches for shortest paths
        while currently_visiting is not None:
            path.insert(0, currently_visiting)

            # fill the shortest path cache:
            if vertex_b not in currently_visiting.shortest_path_cache:
                currently_visiting.shortest_path_cache[vertex_b] = path.copy()

            # move on (i.e., continue to follow the breadcrumbs back)
            currently_visiting = currently_visiting.breadcrumb

        return path

    def shortest_path_length(self, vertex_a, vertex_b):
        """
        Returns the shortest path length from ``vertex_a`` to ``vertex_b``.
        """
        return len(self.shortest_path(vertex_a, vertex_b)) - 1

    def analyze(self):
        """
        Sets instance attributes ``aspl`` and
        ``diameter``.

        For an unconnected graph, we return all zeros or -
        if not running in optimized mode - raise an ``AssertionError``.
        Due to this obscure logic, it is not simply not recommended to
        call this on unconnected graphs.

        The implementations searches calculates just one direction per
        combination of vertices but then sums up the path length twice
        to avoid searching the way back as well:
        (a + a_reverse + b + b_reverse + ...) / [count] ==
        (2*a + 2*b + ...) / 2[count] ==
        2 * (a + b + ...) / 2[count] ==
        (a + b + ...) / [count]
        """
        debug("analyzing graph")

        assert bool(self.vertices), "cannot analyze graph w/o vertices"
        assert (self.aspl is None and self.diameter is None,
                "Found cached analysis data. This incident either "
                "suggests an class-internal bug or incorrect usage.")

        longest_shortest_path = -1
        lengths_sum = 0
        lengths_count = 0

        for vertex_a, vertex_b in combinations(self.vertices, 2):
            length = self.shortest_path_length(vertex_a, vertex_b)
            longest_shortest_path = max(longest_shortest_path, length)
            lengths_sum += length
            lengths_count += 1

        assert lengths_sum > 0, "is this graph unconnected?"
        assert lengths_count > 0, "is this graph unconnected?"

        self.diameter = longest_shortest_path
        self.aspl = lengths_sum/lengths_count

    def edges(self):
        """
        Returns a set of (ordered) tuples, which represent edges.
        """
        edges = set()
        for vertex_a in self.vertices:
            for vertex_b in vertex_a.edges_to:
                if vertex_a < vertex_b:
                    edges.add((vertex_a, vertex_b))
                else:
                    edges.add((vertex_b, vertex_a))
        return edges

    def duplicate(self):
        """
        Returns a (deep) duplicate of this graph.

        ``deepcopy`` of the ``copy`` module is no option, since it soon
        hits the maximum recursion depth.
        """
        debug("duplicating %s", self)

        # create a fresh graph with fresh vertices
        dup = self.__class__(self.order, self.degree)

        # copy over shortest path caches
        for dup_vertex, self_vertex in zip(dup.vertices, self.vertices):
            dup_vertex.shortest_path_cache = (
                self_vertex.shortest_path_cache.copy()
            )

        # duplicate edges
        for vertex_a, vertex_b in self.edges():
            dup.add_edge_unsafe(
                dup.vertices[vertex_a.id],
                dup.vertices[vertex_b.id]
            )

        # copy analysis data
        dup.diameter = self.diameter
        dup.aspl = self.aspl

        return dup

    def ideal(self):
        """
        Returns whether this graph is ideal, with respect to its diameter
        and its average shortest path length.
        """
        if self.diameter is None or self.aspl is None:
            self.analyze()

        if self.diameter > self.diameter_lower_bound:
            return False
        assert self.diameter == self.diameter_lower_bound

        if self.aspl > self.aspl_lower_bound:
            return False
        assert self.aspl == self.aspl_lower_bound

        return True

    def _invalidate_analysis_data(self):
        """
        Unsets "cached" analysis data.
        Meant to be called (once) when modifying a graph.
        """
        assert self.aspl is not None, "analysis data already invalidated"
        assert self.diameter is not None, "analysis data already invalidated"
        self.aspl = None
        self.diameter = None

    def invalidate_shortest_path_caches(self):
        """
        Unsets cached shortests paths relating to the given
        ``modified_vertices``.
        """
        # TODO: in favor of lower complexity, we just drop all caches
        # for now. One could implement a more fine-grained dropping of
        # caches and see (i.e., measure) if that is actually more efficient.
        assert len(self.modified_vertices) > 0, "no vertices modified"
        for vertex in self.vertices:
            vertex.shortest_path_cache.clear()
        self.modified_vertices.clear()
