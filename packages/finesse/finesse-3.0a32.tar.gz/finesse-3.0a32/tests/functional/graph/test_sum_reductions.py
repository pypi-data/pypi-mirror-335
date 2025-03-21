import pytest
from finesse.graph.operator_graph import OperatorGraph


@pytest.fixture
def reduced_graph():
    # ┌───┐  A    ┌───┐   B   ┌───┐        ┌───┐         BA        ┌───┐
    # │ 0 ├──────►│ 1 ├──────►│ 2 │ =====> │ 0 ├──────────────────►│ 2 │
    # └───┘       └─▲─┘       └───┘        └─┬─┘                   └─▲─┘
    #               │C                       │    A  ┌───┐  C ┌───┐  │ BC
    #             ┌─┴─┐                      └──────►│ 1 │◄───┤ 3 ├──┘
    #             │ 3 │                              └───┘    └───┘
    #             └───┘
    graph = OperatorGraph(4)
    graph.add_edge("A", 0, 1)
    graph.add_edge("B", 1, 2)
    graph.add_edge("C", 3, 1)

    steps = []
    N = graph.reduce(reductions=steps)

    assert N == 2, steps
    assert (0, 1, 2) in steps
    assert (3, 1, 2) in steps
    return graph


def test_number_of_edges(reduced_graph):
    assert reduced_graph.number_of_edges == 4, tuple(reduced_graph.edges())


def test_number_of_nodes(reduced_graph):
    assert reduced_graph.number_of_nodes == 4


def test_get_edge_operator_expression(reduced_graph):
    assert tuple(reduced_graph.get_edge_operator_expression(0, 1)) == ("A",)
    assert tuple(reduced_graph.get_edge_operator_expression(0, 2)) == ("*", "A", "B")
    assert tuple(reduced_graph.get_edge_operator_expression(3, 1)) == ("C",)
    assert tuple(reduced_graph.get_edge_operator_expression(3, 2)) == ("*", "C", "B")


def test_number_of_self_loops(reduced_graph):
    assert reduced_graph.number_of_self_loops == 0


def test_in_degree(reduced_graph):
    assert reduced_graph.in_degree(0) == 0
    assert reduced_graph.in_degree(1) == 2
    assert reduced_graph.in_degree(2) == 2
    assert reduced_graph.in_degree(3) == 0


def test_out_degree(reduced_graph):
    assert reduced_graph.out_degree(0) == 2
    assert reduced_graph.out_degree(1) == 0
    assert reduced_graph.out_degree(2) == 0
    assert reduced_graph.out_degree(3) == 2
