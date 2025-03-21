import pytest
from finesse.graph.operator_graph import OperatorGraph


@pytest.fixture
def reduced_graph():
    #     ┌───┐  A    ┌───┐   B   ┌───┐   C   ┌───┐
    #     │ 0 ├──────►│ 1 ├──────►│ 2 │──────►│ 3 │
    #     └───┘       └───┘       └───┘       └───┘
    #
    # After applying the product rule:
    #
    #
    #
    #                   CBA       ┌───┐
    #       ┌────────────────────►│ 3 │
    #       │                     └───┘
    #     ┌─┴─┐         BA        ┌───┐
    #     │ 0 ├──────────────────►│ 2 │
    #     └─┬─┘                   └───┘
    #       │    A    ┌───┐
    #       └────────►│ 1 │
    #                 └───┘
    graph = OperatorGraph(4)
    graph.add_edge("A", 0, 1)
    graph.add_edge("B", 1, 2)
    graph.add_edge("C", 2, 3)
    steps = []
    N = graph.reduce(reductions=steps)
    assert N == 2, steps
    return graph


def test_number_of_nodes(reduced_graph):
    assert reduced_graph.number_of_nodes == 4


def test_get_edge_operator_expression(reduced_graph):
    assert tuple(reduced_graph.get_edge_operator_expression(0, 1)) == ("A",)
    assert tuple(reduced_graph.get_edge_operator_expression(0, 2)) == ("*", "A", "B")
    assert tuple(reduced_graph.get_edge_operator_expression(0, 3)) == (
        "*",
        "A",
        "B",
        "C",
    )


def test_edges(reduced_graph):
    # All edges are from 0 node now
    edges = tuple(reduced_graph.edges())
    assert len(edges) == 3
    for edge in ((0, 1), (0, 2), (0, 3)):
        assert edge in edges


def test_number_of_self_loops(reduced_graph):
    assert reduced_graph.number_of_self_loops == 0


def test_in_degree(reduced_graph):
    assert reduced_graph.in_degree(0) == 0
    assert reduced_graph.in_degree(1) == 1
    assert reduced_graph.in_degree(2) == 1
    assert reduced_graph.in_degree(3) == 1


def test_out_degree(reduced_graph):
    assert reduced_graph.out_degree(0) == 3
    assert reduced_graph.out_degree(1) == 0
    assert reduced_graph.out_degree(2) == 0
    assert reduced_graph.out_degree(3) == 0
