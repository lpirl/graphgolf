# encoding: utf8

"""
This module contains classes that enhance a graph.
"""

from abc import ABCMeta
from random import sample, choice, shuffle
from logging import info, warning
from itertools import combinations



class EnhancerRegistry(object):
    """
    Enhancers register at this class.
    """

    enhancers = set()

    def __init__(self):
        """
        Class can not be instantiated. Please use it's classmethods.
        """
        raise RuntimeError(self.__init__.__doc__)

    @classmethod
    def register(cls, enhancer_cls):
        """
        To be used as decorator for classes to register them.
        """
        return cls.enhancers.add(enhancer_cls)



class AbstractBaseEnhancer(object):
    """
    Provides common functionality for enhancers enhancer.
    """

    __metaclass__ = ABCMeta

    def __init__(self, arg_parser):
        self.arg_parser = arg_parser
        self.args = None

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
        return True

    def enhance(self, best_graph, report_queue):
        """
        Tries to enhance a graph; possibly **IN PLACE**.
        Puts an enhanced graph into the ``report_queue``, when found.
        """
        info("enhancer %s started", self.__class__.__name__)

        # pointless to do anything for completely connected graph
        if best_graph.order-1 <= best_graph.degree:
            info("graph fully connected - no need to do anything")
            return

        while True:

            # get a modified graph
            current_graph = best_graph.duplicate()
            current_graph = self.modify_graph(current_graph)

            if not current_graph:
                warning("%s did not return a graph", self.__class__.__name__)
                return

            # analyze
            current_graph.analyze()
            diameter_diff = current_graph.diameter - best_graph.diameter
            aspl_diff = (current_graph.aspl -
                         best_graph.aspl)
            if ((diameter_diff < 0 and aspl_diff <= 0) or
                    (diameter_diff <= 0 and aspl_diff < 0)):
                info("%s found %s", self.__class__.__name__, current_graph)
                report_queue.put(current_graph)
                return

    @staticmethod
    def modify_graph(graph):
        """
        Modifies and returns ``graph`` - possibly **IN PLACE**.
        """
        raise NotImplementedError("subclass responsibility")



class RandomlyReplaceAPercentageEdgesEnhancer(AbstractBaseEnhancer):
    """
    Removes ``PERCENTAGE`` percent of edges and adds new ones.
    """

    PERCENTAGE = None
    """to be set by subclasses"""

    @classmethod
    def _get_number_of_edges_to_replace(cls, graph):
        return int(cls.PERCENTAGE * (len(graph.vertices)/100))

    def applicable_to(self, graph):
        """
        Returns Boolean, whether this enhancer is applicable to the
        specified ``graph``.
        If we disconnect just one vertex, we'll reconnect it to the
        same other vertex. Pointless. So we require at least 2 vertices
        to be re-connected per iteration.
        """
        return self._get_number_of_edges_to_replace(graph) >= 2

    def modify_graph(self, graph):
        """
        Chooses ``PERCENTAGE`` random vertices removes a random edge and
        adds another one.
        """

        assert self.applicable_to(graph)
        assert graph.order > graph.degree-1

        vertices = graph.vertices
        sample_size = self._get_number_of_edges_to_replace(graph)

        sampled_vertices = sample(vertices, sample_size)

        consider_when_relinking = set()
        """
        set is faster (i.e. timeit) for appending and we need to ensure
        no duplicates anyway
        """

        for vertex in sampled_vertices:
            graph.ensure_can_add_edge(vertex)
            consider_when_relinking.add(vertex)

        graph.add_as_many_random_edges_as_possible(consider_when_relinking)

        return graph



@EnhancerRegistry.register
class RandomlyReplace5PercentEdgesEnhancer(RandomlyReplaceAPercentageEdgesEnhancer):
    """ See ``RandomlyReplaceAPercentageEdgesEnhancer``. """
    PERCENTAGE = 5



@EnhancerRegistry.register
class RandomlyReplace10PercentEdgesEnhancer(RandomlyReplaceAPercentageEdgesEnhancer):
    """ See ``RandomlyReplaceAPercentageEdgesEnhancer``. """
    PERCENTAGE = 10



@EnhancerRegistry.register
class RandomlyReplace50PercentEdgesEnhancer(RandomlyReplaceAPercentageEdgesEnhancer):
    """ See ``RandomlyReplaceAPercentageEdgesEnhancer``. """
    PERCENTAGE = 50



@EnhancerRegistry.register
class ModifyLongestPaths(AbstractBaseEnhancer):
    """
    #. searches longest paths
    #. if source or destination vertex have no ports left, unlink a
       random edge, respectively
    #. randomly relink, considering all vertices
    """

    @classmethod
    def modify_graph(cls, graph):
        """ See class' docstring. """

        hops_count_max = 0
        """
        Stores the maximum count of hops found between any two vertices.
        """

        longest_paths = []
        """
        Stores tuples of (source, destination) vertices, for which one has
        to hop over ``hops_count_max`` vertices (i.e., source and destination
        of the longest paths).
        """

        # find longest paths and remember them
        for vertex_a, vertex_b in combinations(graph.vertices, 2):
            hops = graph.hops(vertex_a, vertex_b)
            hops_count = len(hops)
            if hops_count == hops_count_max:
                longest_paths.append((vertex_a, vertex_b))
            elif hops_count > hops_count_max:
                hops_count_max = hops_count
                longest_paths = [(vertex_a, vertex_b)]
            # elif hops_count < hops_count_max:
                # pass

        # process paths that are of maximum length
        for source_and_dest in longest_paths:

            # process source and destination vertex of one longest path
            for vertex in source_and_dest:

                graph.ensure_can_add_edge(vertex)

        graph.add_as_many_random_edges_as_possible()

        return graph
