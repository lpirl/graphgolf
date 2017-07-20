"""
All elements of a graph.
"""

from logging import debug, warning
from itertools import combinations
from random import shuffle


class GraphPartitionedError(Exception):
    pass


class Vertex(object):
    """
    A vertex in a graph.

    We'll have a lot of those in memory, so store data wisely at the
    instances.
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

        Access patterns to this structure are different. Did some quick
        tests. Lists appeared to perform almost 10% better than sets.
        """

        self.hops_cache = dict()
        """
        A cache for found paths. Stores only intermediate hops.
        Maps target vertices to shortest paths.
        """

        self.dirty = False
        """
        If our ``edges_to`` have been modified but the ``hops_cache``s
        of the other vertices have not been invalidated/updated, this is
        ``True``. Used to defer cache invalidation.
        """

    __hash__ = object.__hash__
    """
    We explicitly re-use ``object``'s ``__hash__`` here, since it is
    faster than providing an own ``id()``-based implementation.
    See also:
    https://docs.python.org/3/reference/datamodel.html#object.__hash__

    Also, if we'd base our hypothetical implementation of ``__hash__``
    on ``self.id`` (what would make sense), we'd have to do some stunts
    to make an instance of ``Vertex`` to work with pickle
    (see `here <https://bugs.python.org/issue1761028>`__).
    """

    def __eq__(self, other):
        """ Called very very often, avoid adding logic. """
        assert (self.id == other.id) == (id(self) == id(other)), \
               "we don't expect to have equal but non-identical vertices!?"
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

    Partly due to the specifics of the challenge linked above, partly
    due to limitations of the implementation, the graph needs to be of
    ``order`` and ``degree`` of at least two.
    """

    def __init__(self, order, degree):
        debug("initializing graph")

        assert order > 1, "graphs of order < 2 not supported"
        assert degree > 1, "graphs of degree < 2 not supported"

        self._order = order
        self._degree = degree

        self._aspl_lower_bound = None
        self._diameter_lower_bound = None

        # to be filled by ``self.analyze()``
        self.diameter = None
        self.aspl = None

        # ``list`` because needs fast iteration
        self.vertices = [Vertex(i) for i in range(order)]

        # if edges modified and vertices' hops caches need to be updated
        self._dirty = False

    def __str__(self):
        bits = [
            self.__class__.__name__, str(hex(id(self))),
            "ASPL=%s" % self.aspl or "n/a",
            "diameter=%s" % self.diameter or "n/a",
        ]
        return " ".join(bits)

    @property
    def order(self):
        """
        Making ``order`` a property via this getter prevents accidental
        modification of the attribute outside ``__init__``.
        """
        return self._order

    @property
    def degree(self):
        """
        Making ``degree`` a property via this getter prevents accidental
        modification of the attribute outside ``__init__``.
        """
        return self._degree

    def _calculate_lower_bounds(self):
        """
        Returns the lower bound of the (diameter, average shortest path
        length) for the given ``order`` and ``degree``.

        Copied from http://research.nii.ac.jp/graphgolf/py/create-random.py
        """

        assert self._aspl_lower_bound is None and \
               self._diameter_lower_bound is None, \
               "lower bounds already calculated"

        order = self._order
        degree = self._degree

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
        if self._aspl_lower_bound is None:
            self._calculate_lower_bounds()
        return self._aspl_lower_bound

    @property
    def diameter_lower_bound(self):
        """
        Returns the lower bound for the diameter for this graph.
        Be aware, that for low values of ``order`` and ``degree``, this
        might return ``None``, due to a lack of implementation.
        """
        if self._diameter_lower_bound is None:
            self._calculate_lower_bounds()
        return self._diameter_lower_bound

    def add_edge_unsafe(self, vertex_a, vertex_b):
        """
        Adds an edge between the two given vertices w/o checking constraints.

        Called often, keep minimal.
        """
        assert vertex_a in self.vertices
        assert vertex_b in self.vertices
        assert vertex_a != vertex_b
        debug("wiring %s and %s", vertex_a, vertex_b)
        vertex_a.edges_to.append(vertex_b)
        vertex_b.edges_to.append(vertex_a)
        self._dirty = True
        vertex_a.dirty = True
        vertex_b.dirty = True
        assert len(vertex_a.edges_to) <= self.degree
        assert len(vertex_b.edges_to) <= self.degree

    def remove_edge_unsafe(self, vertex_a, vertex_b):
        """
        Removes an edge between the two given vertices w/o checking anything.

        Called often, keep minimal.
        """
        debug("de-wiring %s and %s", vertex_a, vertex_b)
        assert vertex_a in self.vertices
        assert vertex_b in self.vertices
        assert vertex_a != vertex_b, "vertex should not have edge to itself"
        vertex_a.edges_to.remove(vertex_b)
        vertex_b.edges_to.remove(vertex_a)
        vertex_a.dirty = True
        vertex_b.dirty = True
        self._dirty = True

    def add_as_many_random_edges_as_possible(self, limit_to_vertices=None):
        """
        Adds random edges to the graph, to the maximum what
         ``self.degree`` allows.
        This implementation targets graphs with no initial edges_to.

        For optimization purposes, this is an terrible all-in-one method.
        """
        debug("connecting graph randomly")

        degree = self._degree

        if limit_to_vertices is not None:
            assert len(limit_to_vertices) == len(set(limit_to_vertices)), \
                   "please make sure there are no duplicates in " \
                   "``limit_to_vertices``"
            overall_vertices = list(limit_to_vertices)
        else:
            overall_vertices = list(self.vertices)
        """
        ``overall_vertices``: A list of vertices that we consider in
        this method. Vertices which were found with no ports left will
        be removed during the execution of this method.
        """

        # repeat ``degree`` times
        for _ in range(degree):

            if len(overall_vertices) < 2:
                break

            current_vertices = list(overall_vertices)
            """
            The list of vertices to add edges to in this 'round'
            (i.e. 'for this degree').
            """

            shuffle(current_vertices)

            # repeat until no(t enough) vertices left
            while len(current_vertices) > 1:

                vertex_a = current_vertices.pop(0)
                debug("searching random connection for %s", vertex_a)

                # honor degree at vertex a
                if len(vertex_a.edges_to) == degree:
                    debug("no ports left")
                    try:
                        # The vertex might be removed already, if it was
                        # found as a "vertex_b" with no ports left.
                        # Since this is usually not the case, we use
                        # the slow try/except as an "optimistic" approach.
                        overall_vertices.remove(vertex_a)
                    except ValueError:
                        pass
                    continue
                assert len(vertex_a.edges_to) < degree

                # search for a vertex to connect to
                # (we iterate via an index to be able to modify the list
                # we iterate over (current_vertices) in place; avoids
                # copying the whole thing.)
                vertex_b_i = 0
                while vertex_b_i < len(current_vertices):
                    vertex_b = current_vertices[vertex_b_i]

                    # honor degree at vertex b
                    if len(vertex_b.edges_to) == degree:
                        debug("vertex b (%s) has no ports left", vertex_b)
                        overall_vertices.remove(vertex_b)
                        current_vertices.pop(vertex_b_i)
                        continue
                    assert len(vertex_b.edges_to) < degree

                    # do not add edges_to that already exist
                    if vertex_b in vertex_a.edges_to:
                        debug("vertex b (%s) already connected", vertex_b)
                        vertex_b_i += 1
                        continue

                    # no constraints violated, let's connect to this vertex
                    self.add_edge_unsafe(vertex_a, vertex_b)
                    break

    def hops(self, vertex_a, vertex_b):
        """
        Returns a minimal number of hops (Breadth-First search) to get
        from ``vertex_a`` to ``vertex_b`` (``vertex_a`` != ``vertex_b``).
        Returns an empty list if ``vertex_a`` and ``vertex_b`` are
        directly connected with an edge.
        Returns ``None`` if no path between ``vertex_a`` and ``vertex_b``
        could be found.

        Raises assertion errors on invalid input. We chose assertions
        because they are skipped when running the interpreter with -O.
        Design your calling code to not call this with invalid input.

        It actually searches the paths always from the lower ID to the
        higher ID vertex to have more hits in the hops caches.
        (We could also fill caches for the reverse direction as well but
        this feels way more complicated)

        Called very often, keep efficient.
        """
        debug("searching shortest path between %s and %s", vertex_a,
              vertex_b)

        assert vertex_a != vertex_b, \
               "won't search hops between a vertex and itself..."

        # we search paths always in one direction (smaller to bigger ID)
        reverse = vertex_a > vertex_b
        if reverse:
            debug("actually searching path reversed")
            vertex_a, vertex_b = vertex_b, vertex_a

        # check if we can serve the request from the cache
        hops_cache_entry = vertex_a.hops_cache.get(vertex_b, None)
        if hops_cache_entry is not None:
            debug("hops cache hit")
            return hops_cache_entry

        # ``list`` because this must be ordered
        # (to not descend accidentally while doing breadth-first search):
        currently_enqueued = [vertex_a]

        # out special hacky semantic to mark the start vertex
        # (saves a comparison in the inner-most loop)
        vertex_a.breadcrumb = vertex_a

        # non-recursive breadth-first walk the graph and lay breadcrumbs
        # until the desired vertex is found
        currently_visiting = None
        while currently_enqueued:
            currently_visiting = currently_enqueued.pop(0)

            # check if we arrived at the target vertex
            if currently_visiting == vertex_b:
                break

            for edge_to in currently_visiting.edges_to:
                if edge_to.breadcrumb is None:
                    assert edge_to != vertex_a, \
                           "should never come across start node"
                    edge_to.breadcrumb = currently_visiting
                    currently_enqueued.append(edge_to)
        else:
            raise GraphPartitionedError()

        # follow back the breadcrumbs and remember the hops taken
        # (excluding departure and destination)
        hops = []

        # skip the target vertex (should not appear in returned hops list)
        currently_visiting = currently_visiting.breadcrumb

        # loop until we arrive at the start vertex (and skip it as well)
        while currently_visiting != vertex_a:

            # fill the hops cache:
            if vertex_b not in currently_visiting.hops_cache:
                currently_visiting.hops_cache[vertex_b] = hops.copy()

            # remember this vertex as hop
            hops.insert(0, currently_visiting)

            # move on (i.e., continue to follow the breadcrumbs back)
            currently_visiting = currently_visiting.breadcrumb

        assert vertex_a not in hops and vertex_b not in hops, \
               "neither start nor destination node should be returned"

        # if we searched reverse, we have to reverse the list of hops we
        # return
        if reverse:
            hops.reverse()

        # vacuum old breadcrumbs
        #   note: we could also re-walk the vertices we touched (by
        #   looking at the breadcrumbs) and reset the breadcrumbs only
        #   for those vertices. However, (for a graph of order 300 and
        #   degree 10), blindly resetting the breadcrumbs of all vertices
        #   took only half the time
        for vertex in self.vertices:
            vertex.breadcrumb = None

        return hops

    def hops_count(self, vertex_a, vertex_b):
        """
        Returns the minimum number of hops to get from ``vertex_a`` to
        ``vertex_b``.
        Returns ``None`` if there is no connection between ``vertex_a``
        and ``vertex_b``.
        """
        return len(self.hops(vertex_a, vertex_b)) + 1

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

        self._invalidate_caches()

        longest_shortest_path = -1
        lengths_sum = 0
        lengths_count = 0

        for vertex_a, vertex_b in combinations(self.vertices, 2):
            length = self.hops_count(vertex_a, vertex_b)
            if longest_shortest_path < length:
                longest_shortest_path = length
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
            dup_vertex.hops_cache = (
                self_vertex.hops_cache.copy()
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

    def _invalidate_caches(self):
        """
        Invalidates internally cached values.

        This is quite expensive. Consider wisely when calling this.
        """
        assert self._dirty, "no vertices modified"

        debug("invalidating hops caches")
        self.aspl = None
        self.diameter = None

        # We look into the hops caches of all vertices. If we find a
        # modified vertex as target or as hop, we drop that cache item.

        # loop over all vertices (we have to check *all* the caches):
        for vertex in self.vertices:

            # this is where we store what to invalidate later on:
            # (this pattern avoids copying the hops cache, what would
            # be necessary to modify it while iterating over its elements)
            keys_to_invalidate = set()

            # loop over all cache entries of that vertex:
            for target, hops in vertex.hops_cache.items():

                # check if the target of that cache entry is a modified
                # vertex
                if target.dirty:
                    keys_to_invalidate.add(target)
                    break

                # check if a modified vertex is within the hops
                for hop in hops:
                    if hop.dirty:
                        keys_to_invalidate.add(target)
                        break

            # now actually clear items from the vertex' cache
            for key_to_invalidate in keys_to_invalidate:
                del vertex.hops_cache[key_to_invalidate]

        # reset dirty flags
        for vertex in self.vertices:
            vertex.dirty = False
        self._dirty = False

    def __getstate__(self):
        """
        This is our custom implementation to pickle a graph.
        ``pickle``'s default implementation exceeds the maximum recursion
        depths very soon for bigger graphs.

        Test show, that this implementation is at least fast as the
        generic implementation by the ``pickle`` module.
        """
        debug("collecting state of graph instance")

        # We do not want to transform the iterable of modified vertices to
        # an iterable of IDs. After invalidating the corresponding caches,
        # this iterable will be empty.
        if self._dirty:
            self._invalidate_caches()
        assert not self._dirty

        debug("collecting all attributes but vertices")
        state = {k: v
                 for k, v in self.__dict__.items()
                 if k != "vertices"}

        debug("collecting edge IDs")
        state["edges"] = tuple((a.id, b.id) for a, b in self.edges())

        debug("collecting hops caches of vertices")
        # brutal violation of Demeter's law
        #   a list of hops caches, one per vertex, in order
        #   the caches itself are only ID-based
        state["hops_caches"] = tuple(
            # map a destination to IDs of the "hop vertices"
            # (like ``Vertex``'s  ``hops_cache`` but with IDs).
            {dest.id: tuple(hop.id for hop in hops)
             for dest, hops in vertex.hops_cache.items()}
            for vertex in self.vertices
        )

        return state

    def __setstate__(self, state):
        """
        This is our custom implementation to unpickle a graph.
        See also ``self.__getstate__()``.
        """
        debug("restoring state of graph instance")

        debug("restoring basic attributes")
        self._order = state.pop("_order")
        self._degree = state.pop("_degree")

        debug("restoring vertices")
        self.vertices = [Vertex(i) for i in range(self.order)]
        vertices = self.vertices

        debug("restoring edges")
        for src_id, dest_id in state.pop("edges"):
            self.add_edge_unsafe(vertices[src_id], vertices[dest_id])

        debug("restoring hops caches")
        hops_caches = state.pop("hops_caches")
        assert len(vertices) == len(hops_caches)
        for vertex, hops_cache in zip(vertices, hops_caches):
            vertex.hops_cache = {
                vertices[dest_id]: [vertices[hop_id] for hop_id in hop_ids]
                for dest_id, hop_ids in hops_cache.items()
            }

        debug("restoring remaining attributes")
        for key, value in state.items():
            setattr(self, key, value)
