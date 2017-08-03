
class HopsCache(object):
    """
    A (for out use case) specialized data structure to store hops
    between vertices.

    The idea is to store the hops always in the same direction (vertex
    with lower ID to vertex with higher ID) for optimization.

    It tries to be fast.
    """

    def __init__(self, order):
        """
        ``order`` is the order of the graph, which we need for
        pre-allocation
        """

        self._data = [
            [None] * cache_size
            for cache_size in range(order-1, 0, -1)
        ]
        """
        Since we store the hops from the lower to the higher vertex ID,
        the first vertex, has a maximum of ``order-1`` cache entries,
        the second one ``order-2`` and so on.
        """

    def get(self, a, b):
        """
        Returns hops cache entry between ``a`` and ``b`` or ``None``.
        """
        assert a != b
        if a < b:
            return self._data[a.id][b.id - a.id - 1]
        else:
            hops = self._data[b.id][a.id - b.id - 1]
            if hops is None:
                return None
            return tuple(reversed(hops))

    def set(self, a, b, hops):
        """
        Sets hops cache entry between ``a`` and ``b``.
        """
        assert a != b
        if a < b:
            assert self._data[a.id][b.id - a.id - 1] is None, \
                   "please check why you overwrite this cache entry " \
                   "and clear it manually before, if this is really what " \
                   "you want to do (we usually do not need this)"
            self._data[a.id][b.id - a.id - 1] = hops
        else:
            assert self._data[b.id][a.id - b.id - 1] is None, \
                   "please check why you overwrite this cache entry " \
                   "and clear it manually before, if this is really what " \
                   "you want to do (we usually do not need this)"
            self._data[b.id][a.id - b.id - 1] = tuple(reversed(hops))

    def unset(self, a, b):
        """
        Removes cache entry for hops between ``a`` and ``b``.
        """
        assert a != b
        if b < a:
            a, b = b, a

        assert self._data[a.id][b.id - a.id - 1] is not None, \
                   "please check why you double-unset this cache entry " \
                   "and clear it manually before, if this is really what " \
                   "you want to do (we usually do not need this)"
        self._data[a.id][b.id - a.id - 1] = None

    def clear(self):
        """ Drops all cache entries. """
        for entries in self._data:
            for entry_i, _ in enumerate(entries):
                entries[entry_i] = None

    def ids(self):
        """
        Returns an iterators for all cached values in the style of:
        (
            ( # from vertex 0
                (hop, hop, ...), # to vertex 1
                (hop, hop, ...), # to vertex 2
                ...
            ),
            ( # from vertex 1
                (hop, hop, ...), # to vertex 2
                (hop, hop, ...), # to vertex 3
                ...
            ),
            ...
        )
        """
        return tuple(
            tuple(
                tuple(hop.id for hop in hops)
                for hops in hops_caches
            )
            for hops_caches in self._data
        )

    def set_from_ids(self, ids, vertices):
        """
        "Reverse" of ``ids()``.
        """

        assert len(ids) + 1 == len(vertices)

        for source_id, cache_entries in enumerate(ids):
            for target_id, hop_ids in enumerate(cache_entries):
                self._data[source_id][target_id] = tuple(
                    vertices[hop_id] for hop_id in hop_ids
                )
