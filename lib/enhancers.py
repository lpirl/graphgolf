# encoding: utf8

"""
This module contains classes that enhance a graph.
"""

from abc import ABCMeta
from random import sample
from logging import debug, info, warning
from itertools import combinations, chain

from lib.graph_elements import GraphPartitionedError


class Registry(object):
    """
    s register at this class.
    """

    enhancers = list()

    def __init__(self):
        """
        Class can not be instantiated. Please use it's classmethods.
        """
        raise RuntimeError(self.__init__.__doc__)

    @classmethod
    def register_multiple(cls, times):
        """
        Decorator to register a class multiple times.
        """
        def _register_multiple(enhancer_cls):
            for _ in range(times):
                cls.register(enhancer_cls)
        return _register_multiple

    @classmethod
    def register(cls, enhancer_cls):
        """
        To be used as decorator for classes to register them.
        """
        return cls.enhancers.append(enhancer_cls)



class AbstractBase(object):
    """
    Provides common and helper functionality for enhancers.

    We could also come up with (multi-)inheritance structure, so that
    every enhancer can be equipped with exactly what is needed but
    this can end up quite complex and confusing in relation to relatively
    simple logic (tried it, it's overkill).
    I.e., we put all the helper methods here, no matter which subclasses
    use them.
    """

    __metaclass__ = ABCMeta

    MODIFICATIONS = None
    """
    Number of modifications to apply to graph before throwing the
    modified graph away and start again with the best graph known.

    If ``None``, we'll use ``order*degree``.
    """

    def __init__(self, arg_parser):
        self.arg_parser = arg_parser
        self.args = None


        self.active = True
        """
        Subclasses might want to set this to ``False``, e.g., if there will
        be no more progress.
        """

    def set_args(self, args):
        """
        Called to set the parsed CLI arts for instance.
        """
        self.args = args


    def applicable_to(self, graph):
        """
        Returns Boolean, whether this enhancer is applicable to the
        specified ``graph``.
        """
        # return whether graph is fully connected
        return graph.order > graph.degree-1

    def enhance(self, best_graph, report_queue):
        """
        Tries to enhance a graph; possibly **IN PLACE**.
        Puts an enhanced graph into the ``report_queue``, when found.
        """
        info("enhancer %s started", self.__class__.__name__)

        assert best_graph.aspl is not None and \
               best_graph.diameter is not None, "graph must be analyzed"

        # pointless to do anything for completely connected graph
        if best_graph.order-1 <= best_graph.degree:
            info("graph fully connected - no need to do anything")
            return

        modifications = self.MODIFICATIONS or \
                        int(best_graph.order*best_graph.degree)

        while self.active:

            # get a new copy of best graph to work with
            current_graph = best_graph.duplicate()

            for _ in range(modifications):

                # get a modified graph
                try:
                    current_graph = self.modify_graph(current_graph)
                except GraphPartitionedError:
                    debug("graph partitioned")
                    continue

                if not current_graph:
                    warning("%s did not return a graph", self.__class__.__name__)
                    return

                # analyze
                try:
                    current_graph.analyze()
                except GraphPartitionedError:
                    continue
                if current_graph < best_graph:
                    info("%s found %s", self.__class__.__name__, current_graph)
                    report_queue.put(current_graph)
                    return

    def modify_graph(self, graph):
        """
        Modifies and returns ``graph`` - possibly **IN PLACE**.
        """
        raise NotImplementedError("subclass responsibility")

    def remove_random_edge(self, graph, vertex,
                           allow_complete_disconnect=True):
        """
        Removes a random edge from ``vertex``.
        If not ``allow_complete_disconnect``, this method will take care
        of not disconnecting vertices from the graph completely.

        For your concrete enhancer, please test if the different settings
        for ``allow_complete_disconnect``. I found that allowing to
        disconnect vertices from the graph completely gave better results
        (of course, only if you relink them afterwards).
        """
        for edge_to in sample(vertex.edges_to, len(vertex.edges_to)):
            if len(edge_to.edges_to) > 1 or allow_complete_disconnect:
                graph.remove_edge_unsafe(vertex, edge_to)
                return edge_to

        debug("%s could not find an edge to remove for %s",
              self, vertex)

        return None

    def ensure_can_add_edge(self, graph, vertex):
        """
        Removes a random edge from ``vertex`` if, otherwise, no more
        edge could be connected to it. I.e, if ``vertex`` has already
        ``graph.degree`` edges connected.

        Returns the vertex to which the edge was removed (might be
        ``None``.
        """
        assert len(vertex.edges_to) <= graph.degree

        # check if the vertex has a port left:
        if len(vertex.edges_to) == graph.degree:
            return self.remove_random_edge(graph, vertex)

    def longest_paths(self, graph):
        """
        Returns tuples of (source, destination) vertices, for which one has
        to hop over ``hops_count_max`` vertices (i.e., source and destination
        of the longest paths).
        """

        hops_count_max = 0
        """
        Stores the maximum count of hops found between any two vertices.
        """

        longest_paths = []

        # find longest paths and remember them
        for vertex_a, vertex_b in combinations(graph.vertices, 2):
            hops = graph.hops(vertex_a, vertex_b)
            hops_count = len(hops)
            if hops_count == hops_count_max:
                longest_paths.append((vertex_a, vertex_b))
            elif hops_count > hops_count_max:
                hops_count_max = hops_count
                longest_paths = [(vertex_a, vertex_b)]
            # we don't need to handle the third case:
            # elif hops_count < hops_count_max:
                # pass

        assert len(longest_paths) > 0
        return longest_paths


class AbstractRandomlyRelinkVertices(AbstractBase):
    """
    Helpers that base on the idea to identify vertices of some
    quality (e.g, remote vertices), ensure an edge can be added, and add
    random edges to the graph (what will likely add edges to the
    aforementioned vertices).
    """

    __metaclass__ = ABCMeta

    def vertices_to_consider(self, graph):
        """
        Returns vertices that should receive new edges.
        """
        raise NotImplementedError("subclass responsibility")

    def modify_graph(self, graph):
        """
        Makes sure an edge to every ``vertices_to_consider`` can be added
        and relinks all of them all together.
        See also class' docstring.
        """

        assert self.applicable_to(graph)

        # process paths that are of maximum length
        for vertex in self.vertices_to_consider(graph):
            self.ensure_can_add_edge(graph, vertex)

        # not limiting ``add_as_many_random_edges_as_possible`` to the
        # vertices we modified appeared to give better slower BUT
        # was observed to make progress more reliably
        graph.add_as_many_random_edges_as_possible()

        return graph



class RandomlyRelinkMostDistantVertices(AbstractRandomlyRelinkVertices):
    """
    Randomly relinks source and destination vertex of longest paths.
    """

    def vertices_to_consider(self, graph):
        """ Chained version of ``longest_paths``. """
        return chain.from_iterable(self.longest_paths(graph))



class ConnectMostDistantVertices(AbstractRandomlyRelinkVertices):
    """
    Just like ``RandomlyRelinkMostDistantVertices`` but creates an edge
    between most distant vertices right away.
    """

    def modify_graph(self, graph):
        """
        See class' docstring.MostDis
        """

        assert self.applicable_to(graph)

        # process paths that are of maximum length
        for source_and_dest in self.longest_paths(graph):

            # process source and destination vertex of one longest path
            for vertex in source_and_dest:
                self.ensure_can_add_edge(graph, vertex)
            graph.add_edge_unsafe(*source_and_dest)

        # ``self.ensure_can_add_edge`` might potentially removed edges to
        # vertices other than those in ``source_and_dest``, let's add
        # as many edges as allowed again
        graph.add_as_many_random_edges_as_possible()

        return graph



class RandomlyRelinkMostDistantInTooLongPaths(AbstractRandomlyRelinkVertices):
    """
    Randomly relinks paths that are longer than the diameter lower bound.
    """

    def vertices_to_consider(self, graph):
        """
        Yields tuples of (source, destination) vertices, for which one has
        to hop over more than ``diameter_lower_bound`` vertices
        (i.e., source and destination of "too long" paths).
        """

        if graph.diameter_lower_bound is None:
            graph.analyze()

        for vertex_a, vertex_b in combinations(graph.vertices, 2):
            hops = graph.hops(vertex_a, vertex_b)
            if len(hops)+1 > graph.diameter_lower_bound:
                yield vertex_a
                yield vertex_b



class RandomlyRelinkAllInTooLongPaths(AbstractRandomlyRelinkVertices):
    """
    Randomly relinks paths that are longer than the diameter lower bound.
    """

    def vertices_to_consider(self, graph):
        """
        Yields tuples of (source, destination) vertices, for which one has
        to hop over more than ``diameter_lower_bound`` vertices
        (i.e., source and destination of "too long" paths).
        """

        if graph.diameter_lower_bound is None:
            graph.analyze()

        for vertex_a, vertex_b in combinations(graph.vertices, 2):
            hops = graph.hops(vertex_a, vertex_b)
            if len(hops)+1 > graph.diameter_lower_bound:
                yield vertex_a
                for hop in hops:
                    yield hop
                yield vertex_b



class AbstractRandomlyReplaceRandomEdges(AbstractRandomlyRelinkVertices):
    """
    Removes ``NUMBER_OF_EDGES_TO_REPLACE`` percent of edges and adds new
    ones.
    """

    __metaclass__ = ABCMeta

    NUMBER_OF_EDGES_TO_REPLACE = None
    """to be set by subclasses"""

    def _number_of_edges_to_replace(self, graph):
        """
        Returns the number of edges to replace.
        Subclasses might want to override this.
        """
        return self.NUMBER_OF_EDGES_TO_REPLACE

    def applicable_to(self, graph):
        return (super().applicable_to(graph) and
                self._number_of_edges_to_replace(graph) > 0)

    def vertices_to_consider(self, graph):
        """
        Yields a random sample of size ``_number_of_edges_to_replace``
        of edges to consider.
        """
        return sample(graph.vertices,
                      self._number_of_edges_to_replace(graph))



class AbstractRandomlyReplacePercentageOfEdges(
        AbstractRandomlyReplaceRandomEdges
):
    """
    Like ``AbstractRandomlyReplaceRandomEdges`` but configured via a
    percentage of edges to replace.
    """

    PERCENTAGE = None
    """to be set by subclasses"""

    def _number_of_edges_to_replace(self, graph):
        return int(self.PERCENTAGE * graph.order / 100)



########################################################################
#
# register concrete classes
#

#~ Registry.register_multiple(1)(ConnectMostDistantVertices)
#~ Registry.register_multiple(1)(RandomlyRelinkMostDistantVertices)
#~ Registry.register_multiple(1)(RandomlyRelinkAllInTooLongPaths)
#~ Registry.register_multiple(1)(RandomlyRelinkMostDistantInTooLongPaths)

#~ @Registry.register_multiple(1)
#~ class RandomlyReplaceOneEdge(AbstractRandomlyReplaceRandomEdges):
    #~ """ See ``AbstractRandomlyReplaceRandomEdges``. """
    #~ NUMBER_OF_EDGES_TO_REPLACE = 1

#~ @Registry.register_multiple(1)
#~ class RandomlyReplaceTwoEdges(AbstractRandomlyReplaceRandomEdges):
    #~ """ See ``AbstractRandomlyReplaceRandomEdges``. """
    #~ NUMBER_OF_EDGES_TO_REPLACE = 2

@Registry.register_multiple(1)
class  RandomlyReplaceTenPercentEdges(
        AbstractRandomlyReplacePercentageOfEdges
):
    """ See super class' docstring. """
    PERCENTAGE = 10
