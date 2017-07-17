# encoding: utf8

"""
This module contains classes that enhance a graph.
"""

from abc import ABCMeta
from random import sample, choice
from logging import info



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
                info("%s did not return a graph", self.__class__.__name__)
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

        for vertex_a in sampled_vertices:
            if vertex_a.edges_to:
                vertex_b = choice(vertex_a.edges_to)
                graph.remove_edge_unsafe(vertex_a, vertex_b)
                consider_when_relinking.add(vertex_a)
                consider_when_relinking.add(vertex_b)

        graph.add_as_many_random_edges_as_possible(consider_when_relinking)

        return graph



@EnhancerRegistry.register
class RandomlyReplace1PercentEdgesEnhancer(RandomlyReplaceAPercentageEdgesEnhancer):
    """ See ``RandomlyReplaceAPercentageEdgesEnhancer``. """
    PERCENTAGE = 1



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
