import pytest
from finesse.graph.operator_graph import OperatorGraph


@pytest.fixture
def reduced_graph():
    graph = OperatorGraph(4)
    graph.add_edge("A", 0, 1)
    graph.add_edge("B", 1, 2)
    graph.add_edge("C", 2, 3)
    graph.add_edge("D", 2, 0)
    steps = []
    N = graph.reduce(reductions=steps)
    assert N == 2, steps
    assert (2, 0, 1) in steps
    assert (2, 1, 2) in steps
    return graph


def test_number_of_nodes(reduced_graph):
    assert reduced_graph.number_of_nodes == 4


def test_number_of_edges(reduced_graph):
    assert reduced_graph.number_of_edges == 4


def test_number_of_self_loops(reduced_graph):
    assert reduced_graph.number_of_self_loops == 1


def test_nodes_with_self_loops(reduced_graph):
    assert tuple(reduced_graph.nodes_with_self_loops) == (2,)


def test_self_loop_edges(reduced_graph):
    edges = tuple(reduced_graph.self_loop_edges)
    assert len(edges) == 1
    assert (2, 2) in edges


def test_get_edge_operator_expression(reduced_graph):
    assert tuple(reduced_graph.get_edge_operator_expression(2, 0)) == ("D",)
    assert tuple(reduced_graph.get_edge_operator_expression(2, 1)) == ("*", "D", "A")
    assert tuple(reduced_graph.get_edge_operator_expression(2, 2)) == (
        "*",
        "D",
        "A",
        "B",
    )
    assert tuple(reduced_graph.get_edge_operator_expression(2, 3)) == ("C",)


def test_source_nodes(reduced_graph):
    assert tuple(reduced_graph.source_nodes()) == ()


def test_sink_nodes(reduced_graph):
    assert tuple(reduced_graph.sink_nodes()) == (0, 1, 3)


def test_evaluation_nodes(reduced_graph):
    assert tuple(reduced_graph.evaluation_nodes()) == (2,)


def test_to_networkx(reduced_graph):
    import networkx as nx

    nx_graph = reduced_graph.to_networkx()
    assert isinstance(nx_graph, nx.DiGraph)
    assert nx_graph.number_of_nodes() == 4
    assert nx_graph.number_of_edges() == 4
    assert set(nx_graph.edges()) == {(2, 0), (2, 3), (2, 1), (2, 2)}


def test_find_forkless_paths(reduced_graph):
    paths = reduced_graph.find_forkless_paths()
    assert len(paths) == 0
