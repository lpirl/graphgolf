# encoding: utf8

"""
This module contains classes that enhance a graph.
"""

from abc import ABCMeta
from random import sample
from logging import warning, info
from copy import deepcopy



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

    def run(self, graph):
        """
        Tries to enhance a graph **IN PLACE**.
        """

        # pointless to do anything for completely connected graph
        if graph.order-1 <= graph.degree:
            info("graph fully connected - no need to do anything")
            return

        best_graph = graph
        while True:
            current_graph = deepcopy(best_graph)
            current_graph = self.modify_graph(current_graph)
            if not current_graph:
                warning("%s did not return a graph", self.__class__.__name__)
                return
            current_graph.analzye()
            diameter_diff = current_graph.diameter - best_graph.diameter
            aspl_diff = (current_graph.average_shortest_path_length -
                         best_graph.average_shortest_path_length)
            if ((diameter_diff < 0 and aspl_diff <= 0) or
                    (diameter_diff <= 0 and aspl_diff < 0)):
                print(current_graph, "by", self.__class__.__name__)
                best_graph = current_graph

    @staticmethod
    def _report(graph):
        """
        Called to report a better graph application-wide.
        """
        pass # TODO

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

    def modify_graph(self, graph):
        """
        Chooses PERCENT random vertices removes their "first" edge and
        adds another one.
        """
        vertices = graph.vertices
        sample_size = int(self.PERCENTAGE * (len(vertices)/100))

        assert graph.order > graph.degree-1
        # If we disconnect just one vertex, we'll reconnect it to the
        # same other vertex. Pointless.
        if sample_size < 2:
            warning("graph to small for %s", self.__class__.__name__)
            return

        sampled_vertices = sample(vertices, sample_size)
        consider_when_relinking = []
        for vertex_a in sampled_vertices:
            if vertex_a.edges_to:
                vertex_b = vertex_a.edges_to[0]
                graph.remove_edge_unsafe(vertex_a, vertex_b)
                consider_when_relinking.append(vertex_a)
                consider_when_relinking.append(vertex_b)

        graph.add_as_many_random_edges_as_possible(consider_when_relinking)

        return graph



@EnhancerRegistry.register
class RandomlyReplace10PercentEdgesEnhancer(RandomlyReplaceAPercentageEdgesEnhancer):
    """
    Removes 10 percent of edges and adds new ones.
    """

    PERCENTAGE = 10



@EnhancerRegistry.register
class RandomlyReplace50PercentEdgesEnhancer(RandomlyReplaceAPercentageEdgesEnhancer):
    """
    Removes 10 percent of edges and adds new ones.
    """

    PERCENTAGE = 50
