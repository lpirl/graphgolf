"""
All elements of a graph.
"""

from itertools import chain

class Node(int):
  """
  A node in a graph.
  """
  pass

class Edge(object):
  """
  A(n undirected) edge in a graph.

  For (hopefully) faster comparisons, we sort the associated nodes (a<=b).
  """

  def __init__(self, a, b):
    assert isinstance(a, Node)
    assert isinstance(b, Node)
    self.a, self.b = (a, b) if a<b else (b, a)

class GolfGraph(object):
  """
  A graph specifically crafted for
  `the graph golf challenge <http://research.nii.ac.jp/graphgolf/>`__.
  """
  def __init__(self, order):
    self.order = order
    self.nodes = set(Node(i) for i in range(self.order))
    self.edges = set()

  def add_edge(self, a, b):
    assert 0<=a and a<=self.order
    assert 0<=b and b<=self.order
    self.edges.append(Node(a), Node(b))
