#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

try:
    # PyBGL is available at https://github.com/nokia/PyBGL
    from pybgl.graph        import DirectedGraph, vertices, add_edge, add_vertex, edges, vertices
    from pybgl.graph_dp     import GraphDp
    from pybgl.graphviz     import dotstr_to_html
    from pybgl.html         import html
    from pybgl.ipynb        import in_ipynb
    from pybgl.property_map import make_func_property_map
    WITH_PYBGL = True
except ImportError:
    WITH_PYBGL = False

from minifold.closure import closure, minimal_cover

EDGES1 = {(0, 1), (1, 2), (0, 2), (2, 3), (2, 4), (4, 5), (5, 3)}
EDGES2 = {(0, 1), (0, 1)}
EDGES3 = {(0, 1), (1, 2), (1, 3), (0, 2), (2, 3), (2, 4), (4,4), (4, 5), (5, 2), (5, 3)}

if WITH_PYBGL:
    from minifold.closure import edge_to_pair

    def make_graph(edges_set :set) -> DirectedGraph:
        g = DirectedGraph()
        n = 0
        for (u, v) in edges_set:
            assert u >= 0
            while n <= u:
                add_vertex(g)
                n += 1
            while n <= v:
                add_vertex(g)
                n += 1
            add_edge(u, v, g)
        return g

    G1 = make_graph(EDGES1)
    G2 = make_graph(EDGES2)
    G3 = make_graph(EDGES3)

    def demo_minimal_cover(g :DirectedGraph, min_fds :set):
        if not in_ipynb(): return
        s_dot = GraphDp(
            g,
            dg_default = {"rankdir" : "LR"},
            dpe = {
                "color" : make_func_property_map(lambda e : "darkgreen" if edge_to_pair(e, g) in min_fds else "red"),
                "style" : make_func_property_map(lambda e : "solid" if edge_to_pair(e, g) in min_fds else "dashed"),
            }
        ).to_dot()
        html(dotstr_to_html(s_dot))

def test_closure_g1():
    print("test_closure_g1()")
    assert closure(0, EDGES1) == {0, 1, 2, 3, 4, 5}
    assert closure(1, EDGES1) == {1, 2, 3, 4, 5}
    assert closure(2, EDGES1) == {2, 3, 4, 5}
    assert closure(3, EDGES1) == {3}
    assert closure(4, EDGES1) == {3, 4, 5}
    assert closure(5, EDGES1) == {3, 5}

def test_closure_g2():
    print("test_closure_g2()")
    assert closure(0, EDGES2) == {0, 1}
    assert closure(1, EDGES2) == {1}

def test_closure_g3():
    print("test_closure_g3()")
    assert closure(0, EDGES3) == {0, 1, 2, 3, 4, 5}
    assert closure(1, EDGES3) == {1, 2, 3, 4, 5}
    assert closure(2, EDGES3) == {2, 3, 4, 5}
    assert closure(3, EDGES3) == {3}
    assert closure(4, EDGES3) == {2, 3, 4, 5}
    assert closure(5, EDGES3) == {2, 3, 4, 5}

def test_closure():
    test_closure_g1()
    test_closure_g2()
    test_closure_g3()

def test_minimal_cover_g1():
    print("test_minimal_cover_g1()")
    min_fds = minimal_cover(EDGES1)
    if WITH_PYBGL:
        demo_minimal_cover(G1, min_fds)
    assert min_fds == {(0, 1), (1, 2), (2, 4), (4, 5), (5, 3)}

def test_minimal_cover_g2():
    print("test_minimal_cover_g2()")
    min_fds = minimal_cover(EDGES2)
    if WITH_PYBGL:
        demo_minimal_cover(G2, min_fds)
    assert min_fds == {(0, 1)}

def test_minimal_cover_g3():
    print("test_minimal_cover_g3()")
    min_fds = minimal_cover(EDGES3)
    if WITH_PYBGL:
        demo_minimal_cover(G3, min_fds)
    assert min_fds == {(0, 1), (1, 2), (2, 4), (4, 5), (5, 2), (5, 3)}

def test_minimal_cover():
    test_minimal_cover_g1()
    test_minimal_cover_g2()
    test_minimal_cover_g3()

def test_closure_all():
    test_closure()
    test_minimal_cover()

if __name__ == "__main__":
    test_closure_all()
