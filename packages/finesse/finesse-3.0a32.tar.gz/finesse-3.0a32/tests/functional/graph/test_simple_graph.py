import pytest
from finesse.graph.operator_graph import OperatorGraph


@pytest.fixture
def simple_graph():
    graph = OperatorGraph(4)
    graph.add_edge("A.FrR", 0, 1)
    graph.add_edge("A.BkR", 2, 3)
    graph.add_edge("A.FrBkT", 0, 3)
    graph.add_edge("A.BkFrT", 2, 1)
    return graph


def test_number_of_nodes(simple_graph):
    assert simple_graph.number_of_nodes == 4


def test_number_of_edges(simple_graph):
    assert simple_graph.number_of_edges == 4


def test_edges(simple_graph):
    edges = tuple(simple_graph.edges())
    assert len(edges) == 4
    for edge in ((0, 1), (2, 3), (0, 3), (2, 1)):
        assert edge in edges


@pytest.mark.parametrize("node, number", [(0, 2), (1, 0), (2, 2), (3, 0)])
def test_output_edges(simple_graph, node, number):
    edges = tuple(simple_graph.output_edges(node))
    assert len(edges) == number


@pytest.mark.parametrize("node, number", [(0, 0), (1, 2), (2, 0), (3, 2)])
def test_input_edges(simple_graph, node, number):
    edges = tuple(simple_graph.input_edges(node))
    assert len(edges) == number


def test_get_edge_operator_expression(simple_graph):
    assert simple_graph.get_edge_operator_expression(0, 1) == ("A.FrR",)
    assert simple_graph.get_edge_operator_expression(2, 3) == ("A.BkR",)
    assert simple_graph.get_edge_operator_expression(0, 3) == ("A.FrBkT",)
    assert simple_graph.get_edge_operator_expression(2, 1) == ("A.BkFrT",)


def test_number_of_self_loops(simple_graph):
    assert simple_graph.number_of_self_loops == 0


def test_nodes_with_self_loops(simple_graph):
    assert tuple(simple_graph.nodes_with_self_loops) == ()


def test_has_self_loop(simple_graph):
    assert not simple_graph.has_self_loop(0)
    assert not simple_graph.has_self_loop(1)
    assert not simple_graph.has_self_loop(2)
    assert not simple_graph.has_self_loop(3)


def test_in_degree(simple_graph):
    assert simple_graph.in_degree(0) == 0
    assert simple_graph.in_degree(1) == 2
    assert simple_graph.in_degree(2) == 0
    assert simple_graph.in_degree(3) == 2


def test_out_degree(simple_graph):
    assert simple_graph.out_degree(0) == 2
    assert simple_graph.out_degree(1) == 0
    assert simple_graph.out_degree(2) == 2
    assert simple_graph.out_degree(3) == 0


def test_evaluation_nodes(simple_graph):
    assert tuple(simple_graph.evaluation_nodes()) == ()


def test_source_nodes(simple_graph):
    assert tuple(simple_graph.source_nodes()) == (0, 2)


def test_sink_nodes(simple_graph):
    assert tuple(simple_graph.sink_nodes()) == (1, 3)


def test_isolated_nodes(simple_graph):
    assert tuple(simple_graph.isolated_nodes()) == ()


def test_to_networkx(simple_graph):
    import networkx as nx

    nx_graph = simple_graph.to_networkx()
    assert isinstance(nx_graph, nx.DiGraph)
    assert nx_graph.number_of_nodes() == 4
    assert nx_graph.number_of_edges() == 4

    for edge in ((0, 1), (2, 3), (0, 3), (2, 1)):
        assert nx_graph.has_edge(*edge)

    assert nx_graph.in_degree(0) == 0
    assert nx_graph.in_degree(1) == 2
    assert nx_graph.in_degree(2) == 0
    assert nx_graph.in_degree(3) == 2
    assert nx_graph.out_degree(0) == 2
    assert nx_graph.out_degree(1) == 0
    assert nx_graph.out_degree(2) == 2
    assert nx_graph.out_degree(3) == 0


def test_operator_name():
    name = "kyBN4P6ileZCFNIljW8FTZ1ibUhcUxmqiixti55U9reZ7ecWuV653z1JFUvDpTRZ"
    graph = OperatorGraph(2)
    graph.add_edge(name, 0, 1)
    ops = graph.get_edge_operator_expression(0, 1)
    assert ops == (name,), ops
