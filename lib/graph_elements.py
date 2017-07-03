"""
All elements of a graph.
"""

from itertools import chain



class Vertex(object):
  """
  A node in a graph.
  """

  def __init__(self, id, num_ports):
    self.id = id
    self.num_ports = num_ports
    self._related = set()

  def __hash__(self):
    return self.id

  def __lt__(self, other):
    return self.id < other.id

  def __eq__(self, other):
    return self.id == other.id

  def add_related_bidirectional(self, other):
    assert isinstance(other, Vertex)
    self._related.add(other)
    other._related.add(self)
    assert len(self._related) <= self.num_ports

  @property
  def related(self):
    return self._related



class GolfGraph(object):
  """
  A graph specifically crafted for
  `the graph golf challenge <http://research.nii.ac.jp/graphgolf/>`__.
  """

  def __init__(self, order, degree):
    self.order = order
    self.degree = degree
    self.vertices = [Vertex(i, degree) for i in range(order)]

  def add_edge(self, vertex_a, vertex_b):
    self.vertices[vertex_a.id].add_related_bidirectional(vertex_b)
