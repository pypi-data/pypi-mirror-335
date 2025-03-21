import pytest
from finesse.graph.operator_graph import OperatorGraph


@pytest.fixture
def reduced_graph():
    #                   C
    #                  ┌─┐
    #                  ▼ │
    #     ┌───┐  A    ┌──┴┐   B   ┌───┐
    #     │ 0 ├──────►│ 1 ├──────►│ 2 │
    #     └───┘       └───┘       └───┘
    # Nothing should be reduced here as there is a self loop on 1
    graph = OperatorGraph(3)
    graph.add_edge("A", 0, 1)
    graph.add_edge("B", 1, 2)
    graph.add_edge("C", 1, 1)
    steps = []
    N = graph.reduce(reductions=steps)
    assert N == 0, steps
    return graph


def test_number_of_nodes(reduced_graph):
    assert reduced_graph.number_of_nodes == 3


def test_get_edge_operator_expression(reduced_graph):
    assert tuple(reduced_graph.get_edge_operator_expression(1, 1)) == ("C",)
    assert tuple(reduced_graph.get_edge_operator_expression(0, 1)) == ("A",)
    assert tuple(reduced_graph.get_edge_operator_expression(1, 2)) == ("B",)


def test_edges(reduced_graph):
    edges = tuple(reduced_graph.edges())
    assert len(edges) == 3
    for edge in ((0, 1), (1, 2), (1, 1)):
        assert edge in edges


def test_number_of_self_loops(reduced_graph):
    assert reduced_graph.number_of_self_loops == 1


def test_in_degree(reduced_graph):
    assert reduced_graph.in_degree(0) == 0
    assert reduced_graph.in_degree(1) == 2
    assert reduced_graph.in_degree(2) == 1


def test_out_degree(reduced_graph):
    assert reduced_graph.out_degree(0) == 1
    assert reduced_graph.out_degree(1) == 2
    assert reduced_graph.out_degree(2) == 0
