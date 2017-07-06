# encoding: utf8

"""
This module contains classes that enhance a graph.
"""

from abc import ABCMeta
from logging import info, debug

from lib.graph_elements import GolfGraph



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
        best_graph = graph
        while True:
            current_graph = self.modify_graph(best_graph)
            current_graph.analzye()
            if (current_graph.diameter < best_graph.diameter or
                (current_graph.average_shortest_path_length <
                 best_graph.average_shortest_path_length)):
                    info("found a better graph: ASPL=%s, diameter=%s",
                         current_graph.average_shortest_path_length,
                         current_graph.diameter)
                    best_graph = current_graph

    @staticmethod
    def _report(graph):
        """
        Called to report a better graph application-wide.
        """
        raise NotImplementedError("todo")

    @staticmethod
    def modify_graph(graph):
        """
        Modifies and returns ``graph`` - possibly **IN PLACE**.
        """
        raise NotImplementedError("subclass responsibility")



@EnhancerRegistry.register
class RandomEnhancer(AbstractBaseEnhancer):
    """
    Just rebuilds a random graph and checks if its an enhancement.
    """

    def modify_graph(self, graph):
        new_graph = GolfGraph(graph.order, graph.degree)
        new_graph.add_as_many_random_edges_as_possible()
        return new_graph
