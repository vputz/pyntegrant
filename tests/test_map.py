from pyntegrant.map import PRef, SystemMap, dependency_graph
from networkx import topological_sort

def test_dependency_graph():
    m = dict(a=dict(arg1=1, arg2=PRef("b")), b=dict(arg1=PRef("c")))
    g = dependency_graph(m)
    assert list(topological_sort(g)) == ['a','b','c']
