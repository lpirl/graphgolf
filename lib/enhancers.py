# encoding: utf8

"""
This module contains classes that enhance a graph.
"""

from abc import ABCMeta



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
        return enhancers.add(enhancer_cls)



class AbstractBaseEnhancer(object):
    """
    Provides common functionality for enhancers enhancer.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, args_parser):
        self.args_parser = args_parser
        self.args = None

    def set_args(self, args):
        """
        Called to set the parsed CLI arts for instance.
        """
        self.args = args

    def enhance(self, graph, average_shortest_path_length, diameter):
        """
        Tries to enhance a graph **IN PLACE**.
        """
        raise NotImplementedError
