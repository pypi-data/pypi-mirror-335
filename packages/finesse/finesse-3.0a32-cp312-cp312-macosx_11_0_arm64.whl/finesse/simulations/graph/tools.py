import finesse
from finesse.graph import OperatorGraph
from finesse.components import Connector
from finesse.symbols import simplification, Constant, Variable
from finesse.parameter import ParameterRef

import numpy as np
from numbers import Number
from typing import Iterable
from functools import reduce


def make_optical_operator_graph(model: finesse.model.Model) -> OperatorGraph:
    """Create an optical operator graph based on the given model.

    Parameters
    ----------
    model : :class:`finesse.model.Model`
        The model object containing the optical network.

    Returns
    -------
    tuple
        A tuple containing the following elements:
        - node_index : dict
            A dictionary mapping nodes to their corresponding indices.
        - index_name : dict
            A dictionary mapping indices to their corresponding nodes.
        - elements : set
            A set of unique elements in the optical network.
        - graph :class:`finesse.graph.OperatorGraph`
            An operator graph representing the optical network.
    """
    network = model.optical_network

    N_nodes = len(network.nodes)
    node_index = {node: i for i, node in enumerate(network.nodes)}
    index_name = {i: node for i, node in enumerate(network.nodes)}

    graph = OperatorGraph(N_nodes)
    elements = set()

    for a, b in network.edges:
        data = model.optical_network[a][b]
        elements.add(data["owner"]())

        graph.add_edge(
            data["owner"]().name + "." + data["name"],
            node_index[a],
            node_index[b],
        )

    return node_index, index_name, elements, graph


def get_all_optical_equations(elements: Iterable[Connector]) -> dict:
    """Get all optical equations from a list of elements.

    Parameters
    ----------
    elements : Iterable[Connector]
        A list of Connector objects representing the elements.

    Returns
    -------
    dict
        A dictionary containing all the optical equations, where the keys are the equations' names
        and the values are the equations themselves.
    """
    optical_equations = {}
    for element in elements:
        optical_equations.update(element.optical_equations())
    return optical_equations


def expression_tuple_to_symbolic(expr, optical_equations):
    """Converts an expression tuple to a symbolic expression using the provided optical
    equations.

    Parameters
    ----------
    expr : tuple
        The expression tuple to be converted.
    optical_equations : dict
        A dictionary containing the optical equations.

    Returns
    -------
    finesse.symbols.Symbol
        The simplified symbolic expression.

    Notes
    -----
    This function recursively converts an expression tuple into a symbolic expression using the provided optical equations.
    The expression tuple can contain operators such as '+' and '*', and operands that are either symbols or values.
    The optical equations dictionary maps symbols to their corresponding symbolic expressions.

    Examples
    --------
    >>> from finesse.symbols import Variable
    >>> optical_equations = {'a': Variable('a'), 'b': Variable('b')}
    >>> expr = ('+', ('*', 'a', 2), ('*', 'b', 3))
    >>> expression_tuple_to_symbolic(expr, optical_equations)
    2*a + 3*b
    """

    def simplify(expr):
        if isinstance(expr, tuple):
            operator, *operands = expr
            if operator == "+":
                return reduce(np.add, map(simplify, operands))
            elif operator == "*":
                return reduce(np.multiply, map(simplify, operands))
            elif len(expr) == 1:
                return optical_equations[expr[0]]
            else:
                raise Exception(f"Unexpected expr {expr}")
        else:
            return optical_equations[expr]

    with simplification(True):
        y = simplify(expr)
        if isinstance(y, Number):
            return Constant(y)
        else:
            return y


def make_symbolic_optical_operators(
    graph: OperatorGraph,
    optical_equations: dict,
    include_edges: Iterable[tuple[int, int]] = None,
) -> dict:
    """Calculate symbolic optical operators for a given graph and optical equations.

    Parameters
    ----------
    graph : OperatorGraph
        The graph representing the optical system.
    optical_equations : dict
        A dictionary mapping operator names to their corresponding optical equations.
    include_edges : Iterable[tuple[int, int]], optional
        The edges for which to calculate the operators. If not provided, all edges in the graph will be used.

    Returns
    -------
    dict
        A dictionary mapping edge tuples to their corresponding symbolic operators.
    """
    if include_edges is None:
        include_edges = tuple(graph.edges())

    operators = {}
    for a, b in include_edges:
        operators[(a, b)] = 1
        expr = graph.get_edge_operator_expression(a, b)
        operators[(a, b)] = expression_tuple_to_symbolic(expr, optical_equations)

    return operators


def evaluate_non_changing_symbols(equations: dict, substitutions: dict = None):
    """Evaluate the non-changing symbols in the given equations.

    Parameters
    ----------
    equations : dict
        A dictionary containing the equations to be evaluated. The keys represent
        the edges, and the values represent the expressions.

    Returns
    -------
    dict
        A dictionary containing the results of evaluating the non-changing symbols.
        The keys represent the edges, and the values represent the evaluated
        expressions.
    """
    result = {}
    for edge, expr in equations.items():
        result[edge] = expr.expand_symbols().eval(
            keep_changing_symbols=True, subs=substitutions
        )
        if hasattr(result[edge], "expand"):
            result[edge] = result[edge].expand()
        if hasattr(result[edge], "collect"):
            result[edge] = result[edge].collect()
        if isinstance(result[edge], Number):
            result[edge] = Constant(result[edge])

    return result


def get_cavities(graph: OperatorGraph):
    """Get the cavities (self loops) and their coupling status from an OperatorGraph.

    Parameters
    ----------
    graph : OperatorGraph
        The OperatorGraph representing the system.

    Returns
    -------
    cavities : tuple
        A tuple of node indices which have self loops in the graph.
    coupled : tuple
        A tuple indicating the whether a self loop is coupled to another or not
    """
    import networkx as nx

    cycles = tuple(nx.simple_cycles(graph.to_networkx()))
    cavities = tuple(c[0] for c in cycles if len(c) == 1)
    couplings = tuple(c for c in cycles if len(c) >= 2)
    coupled = tuple(any(c in cc for cc in couplings) for c in cavities)
    return cavities, coupled


class ModelOperatorPicture:
    """A picture of the current model state in terms of operators applied in a reduced
    graph. The graph consists of each optical node and the edges are operators
    describing how optical fields propagate between nodes. Any operators that are zero
    will be removed from the graph.

    Attributes
    ----------
    node_index : dict
        A dictionary mapping node names to their indices.
    index_name : dict
        A dictionary mapping node indices to their names.
    elements : list
        A list of optical elements in the model.
    graph : finesse.model.Graph
        A reduced graph representation of the optical model.
    N_reductions : int
        The number of reductions performed on the graph.
    model_constants : dict
        A dictionary of model constants.
    optical_equations : dict
        A dictionary of all optical equations in the model.
    evald_optical_equations : dict
        A dictionary of evaluated optical equations keeping any changing symbols.
    operators : dict
        A dictionary of symbolic optical operators for each edge in `graph`
    non_numeric_symbols : list
        A list of non-numeric symbols in the model.
    changing_symbols : tuple
        A tuple of symbols that are changing in the model.
    """

    def __init__(self, model: finesse.model.Model, evaluate=True, reduce=True):
        self.model = model
        (
            self.node_index,
            self.index_name,
            self.elements,
            self.graph,
        ) = make_optical_operator_graph(model)

        self.model_constants = {
            "_f0_": model._settings.f0,
        }

        self.optical_equations = get_all_optical_equations(self.elements)
        if evaluate:
            self.evald_optical_equations = evaluate_non_changing_symbols(
                self.optical_equations, self.model_constants
            )
        else:
            self.evald_optical_equations = self.optical_equations

        # Find all operators that are definitely zero and
        self.zeroed_edges = []
        for name, expr in self.evald_optical_equations.items():
            if expr == 0:
                el, conn = name.split(".")
                A, B = self.model.get_element(el)._registered_connections[conn]
                Aidx = self.node_index[A]
                Bidx = self.node_index[B]
                self.zeroed_edges.append((Aidx, Bidx))
                self.graph.remove_edge(Aidx, Bidx)

        # Now with a bunch of zero edges removed, we can reduce the graph
        self.N_reductions = self.graph.reduce() if reduce else 0

        # Then compute the final reduce graph operators
        self.operators = make_symbolic_optical_operators(
            self.graph, self.evald_optical_equations
        )

        # Check if we have any zero operators, and if so, remove them
        for key in tuple(self.operators.keys()):
            if self.operators[key] == 0:
                self.graph.remove_edge(*key)
                del self.operators[key]

        self.non_numeric_symbols = set()
        for expr in self.evald_optical_equations.values():
            self.non_numeric_symbols.update(
                expr.all(
                    lambda a: isinstance(a, (Variable, ParameterRef))
                    or (isinstance(a, Constant) and a.is_named)
                )
            )
        # Stop arbitrary set ordering
        self.non_numeric_symbols = list(self.non_numeric_symbols)
        self.non_numeric_symbols.sort(key=lambda s: s.name)
        self.non_numeric_symbols = tuple(self.non_numeric_symbols)

        self.changing_symbols = tuple(
            s for s in self.non_numeric_symbols if s.is_changing
        )

    def solve(
        self, node_index: int or str, source_nodes: Iterable[int or str]
    ) -> finesse.symbols.Symbol:
        """Computes a symbolic solutions for a given node within the graph. This does
        not solve for the actual values of the symbols, linear operatores will be left
        as is. No actual linear operation inversions will take place.

        Parameters
        ----------
        node_index : int|str
            The index of the node to solve for, or string name of node, see. self.node_index.
        source_nodes : Iterable[int or str]
            The indices of source nodes indices or string names that should be included

        Returns
        -------
        :class:`finesse.symbols.Symbol`
            The solution for the specified node

        Examples
        --------
        Plot network but shade out sink nodes:

        >>> import finesse
        >>> from finesse.simulations.graph.tools import ModelOperatorPicture
        >>> model = finesse.script.parse('''
        ...                  l l1
        ...                  bs bs
        ...                  m itmx
        ...                  m itmy
        ...                  link(l1, 1, bs.p1)
        ...                  link(bs.p2, 1, itmy)
        ...                  link(bs.p3, 1, itmx)
        ...                  ''')
        >>> op = ModelOperatorPicture(model, True,True)
        >>> op.graph.plot(alpha_nodes=op.graph.sink_nodes());

        Or just ignore sink nodes all together:

        >>> op.graph.plot(ignore_nodes=[1, 2, 3]);
        """
        if isinstance(node_index, str):
            node_index = self.node_index[node_index]

        source_nodes = [
            (n if isinstance(n, int) else self.node_index[n]) for n in source_nodes
        ]

        def _solve(node_index, source_nodes):
            if self.graph.in_degree(node_index) == 0:
                # Source node solutions are easy, it's either 1 to
                # include it or 0 to exclude it
                if node_index in source_nodes:
                    return Variable(f"E_{{{node_index}}}")
                else:
                    return Constant(0)

            # This is the self loop rule for graph reduction: any self loop is replaced
            # by 1/(1-self_loop_gain) to any incoming edge that is not a self loop
            if self.graph.has_self_loop(node_index):
                self_loop_op = self.operators[(node_index, node_index)]
                CLG = 1 / (1 - self_loop_op)
            else:
                CLG = 1

            term = 0
            # loop through all incoming edges for this node and sum up the results
            # This is recursive as any of the incoming nodes that are not source nodes
            # will also have edges that need to be summed up
            for edge in self.graph.input_edges(node_index):
                if edge[0] != edge[1]:  # not a self-loop
                    term += CLG * self.operators[edge] * _solve(edge[0], source_nodes)

            return term

        with finesse.symbols.simplification(True):
            # Always run with simplification enabled otherwise it will be a mess
            return _solve(node_index, source_nodes)
