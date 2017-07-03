"""
All elements of a graph.
"""



class Vertex(object):
  """
  A node in a graph.
  Keep this minimal.
  """

  def __init__(self, id):
    self.id = id
    self.related = list()

  def __hash__(self):
    return self.id

  def __eq__(self, other):
    return self.id == other.id



class GolfGraph(object):
  """
  A graph specifically crafted for
  `the graph golf challenge <http://research.nii.ac.jp/graphgolf/>`__.
  """

  def __init__(self, order, degree):
    self.order = order
    self.degree = degree

    self.vertices = [Vertex(i) for i in range(order)]

  def add_edge(self, vertex_a, vertex_b):
    assert vertex_a != vertex_b
    vertex_a.related.append(vertex_b)
    vertex_b.related.append(vertex_a)
    assert len(vertex_a.related) <= self.degree
    assert len(vertex_b.related) <= self.degree
