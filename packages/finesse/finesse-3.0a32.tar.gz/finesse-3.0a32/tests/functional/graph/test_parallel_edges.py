from finesse.simulations.graph.tools import OperatorGraph


def test_get_reduced_operator_expression():
    graph = OperatorGraph(4)
    graph.add_edge("A", 0, 1)
    graph.add_edge("B", 1, 2)
    graph.add_edge("C", 2, 3)
    graph.add_edge("D", 2, 3)
    steps = []
    graph.reduce(reductions=steps)

    expr = graph.get_edge_operator_expression(0, 3)
    assert expr == ("*", "A", "B", ("+", "C", "D")), expr


def test_reduced_parallel_with_serial():
    graph = OperatorGraph(4)
    graph.add_edge("a", 0, 1)
    graph.add_edge("b", 1, 2)

    graph.add_edge("c", 0, 3)
    graph.add_edge("d", 3, 2)

    graph.reduce()
    expr = graph.get_edge_operator_expression(0, 2)
    assert expr == ("+", ("*", "a", "b"), ("*", "c", "d")), expr


def test_reduced_linear_parallel():
    graph = OperatorGraph(4)
    graph.add_edge("a", 0, 1)
    graph.add_edge("b1", 1, 2)
    graph.add_edge("b2", 1, 2)
    graph.add_edge("d", 2, 3)

    graph.reduce()
    assert graph.get_edge_operator_expression(0, 3) == (
        "*",
        "a",
        ("+", "b1", "b2"),
        "d",
    )
