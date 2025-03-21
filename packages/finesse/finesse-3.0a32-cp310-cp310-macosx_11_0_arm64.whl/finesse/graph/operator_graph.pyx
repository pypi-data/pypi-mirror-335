cimport numpy as np
import numpy as np
from cpython.ref cimport PyObject
from libc.stdlib cimport free


cdef expression_node_to_tuple_form(ExpressionNode* node, dict value_map):
    """
    Converts an ExpressionNode to a tuple representation. This is a representation
    of the expression tree with nested tuples. The first element of the tuple is
    the operator and the remaining elements are the operands, see Examples section
    below for more details.

    Parameters
    ----------
    node : ExpressionNode*
        The ExpressionNode to convert.
    value_map : dict
        A dictionary mapping values to names. If provided, the values in the
        ExpressionNode are replaced with their corresponding mapping.

    Returns
    -------
    Tuple
        The tuple representation of the ExpressionNode. See Example section

    Example
    -------
    >>> one = create_value_node(1)
    >>> expression_node_to_tuple_form(mul, {})
    (1,)
    >>> add = create_op_node(ADD, 3)
    >>> add_operand(add, create_value_node(1))
    >>> add_operand(add, create_value_node(2))
    >>> add_operand(add, create_value_node(3))
    >>> // add -> 1+2+3
    >>> mul = create_op_node(MUL, 2)
    >>> add_operand(mul, create_value_node(4))
    >>> add_operand(mul, add)
    >>> // mul -> 4*(1+2+3)
    >>> expression_node_to_tuple_form(mul, {})
    ('*', 4, ('+', 1, 2, 3))

    >>> expression_node_to_tuple_form(mul, value_map={1:'a', 2:'b', 3:'c', 4:'d'})
    ('*', 'd', ('+', 'a', 'b', 'c'))
    """
    cdef int i
    if node.type == VALUE:
        if value_map is not None:
            return value_map[node.data.value]
        else:
            return node.data.value
    elif node.type in (ADD, MUL):
        if node.type == ADD:
            operator = "+"
        elif node.type == MUL:
            operator = "*"
        else:
            raise ValueError("Invalid operator type")
        operands = tuple(expression_node_to_tuple_form(node.data.op.operands[i], value_map) for i in range(node.data.op.num_operands))
        return tuple((operator, *operands))


cdef class PyObjectPointer:
    cdef PyObject* ptr


cdef class OperatorGraph:
    """A class representing a graph of linear operators.

    This class provides methods for creating, manipulating, and analyzing a graph
    of linear operators. The graph is represented using an adjacency list data
    structure, where each node represents a state and each edge represents a linear
    operator connecting two states.

    Parameters
    ----------
    num_nodes : int
        The number of nodes in the graph.

    Attributes
    ----------
    graph : Graph
        The underlying graph data structure.
    operator_indices : dict
        A dictionary mapping operator names to their corresponding indices.
    indices_operator_names : dict
        A dictionary mapping indices to their corresponding operator names.

    Methods
    -------
    _validate_node(node)
        Validates if a given node index is within the valid range.
    number_of_nodes()
        Returns the number of nodes in the graph.
    number_of_edges()
        Returns the number of edges in the graph.
    edges()
        Returns an iterator over all edges in the graph.
    output_edges(from_node)
        Returns an iterator over the outgoing edges at a particular node.
    input_edges(node)
        Returns an iterator over the input edges at a particular node.
    print_graph()
        Prints the graph.
    add_edge(name, from_node, to_node)
        Adds an edge to the graph.
    remove_edge(from_node, to_node)
        Removes an edge from the graph.
    get_edge_operator_expression(from_node, to_node)
        Returns a list presentation of the operator expression associated with an edge.
    number_of_self_loops()
        Returns the number of self-loops in the graph.
    nodes_with_self_loops()
        Returns the nodes in the graph that have self-loops.
    self_loop_edges()
        Returns the edges in the graph that are self-loops.
    has_self_loop(node)
        Checks if a node has a self-loop.
    in_degree(node)
        Returns the in-degree of a node.
    out_degree(node)
        Returns the out-degree of a node.
    fix_node(node, state)
        Fixes a node to a specific state.
    next_reducible_node()
        Returns a node index that can be reduced
    evaluation_nodes(ignore_self_loops)
        Returns the nodes that have both inputs and outputs in the graph.
    sum_rule(node)
        Applies the sum reduction rule to a node.
    split_rule(node)
        Applies the split reduction rule to a node.
    fan_rule(node)
        Applies the fan reduction rule to a node.
    series_rule(node)
        Applies the series reduction rule to a node.
    """

    def __init__(self, num_nodes):
        self.graph = create_graph(num_nodes)
        self.operator_indices = {}
        self.indices_operator_names = {}

    def _validate_node(self, node):
        if node < 0 or node >= self.graph.num_nodes:
            raise Exception(f"Node {node} must be between 0 and {self.graph.num_nodes-1}")

    @property
    def number_of_nodes(self):
        return int(self.graph.num_nodes)

    @property
    def number_of_edges(self):
        return int(self.graph.num_edges)

    def edges(self):
        """An iterator over all edges"""
        for i in range(self.number_of_nodes):
            for edge in self.output_edges(i):
                yield edge

    def output_edges(self, from_node):
        """An iterator over the outgoing edges at a particular node
        """
        self._validate_node(from_node)
        cdef int ifrom_node = int(from_node)
        cdef Edge* current = self.graph.output_edges[ifrom_node]

        edges = []
        while (current != NULL):
            edges.append((current.from_node, current.to_node))
            current = current.next

        return edges

    def input_edges(self, node):
        """An iterator over the input edges at a particular node
        """
        self._validate_node(node)
        cdef int ifrom_node = int(node)
        cdef ListItem* current = self.graph.input_edges[ifrom_node]
        cdef Edge *edge = NULL
        edges = []

        while (current != NULL):
            if current.ptr == NULL:
                raise Exception("No edge atttached")
            edge = <Edge*>current.ptr
            edges.append((edge.from_node, edge.to_node))
            current = current.next
        return edges

    def print_graph(self):
        print_graph(self.graph)

    def add_edge(self, name : str, from_node : int, to_node : int):
        """Add an edge to the graph.

        This method adds an edge from `from_node` to `to_node` in the graph. The edge is
        associated with a linear operator named `name`. If the edge already exists in the graph,
        or if an error occurs while adding the edge, an exception is raised.

        The added linear operator is given a monotonically increasing ID value, starting from 0.
        See `.operator_indices` for a mapping of operator names to operator IDs and
        `.indices_operator_names` for a mapping of operator IDs to operator names.

        Parameters
        ----------
        name : str
            The name of the linear operator associated with the edge.
        from_node : int
            The index of the node where the edge starts.
        to_node : int
            The index of the node where the edge ends.

        Raises
        ------
        Exception
            If the edge already exists in the graph (error code -4), or if an error occurs while
            adding the edge (any positive error code).

        """
        if name in self.operator_indices:
            raise KeyError(f"Operator {name} already exists in the graph")

        op_id = self.operator_indices[name] = len(self.operator_indices)
        self.indices_operator_names[op_id] = name

        self._validate_node(from_node)
        self._validate_node(to_node)

        cdef LinearOperator *op = create_linear_operator(op_id)
        if op == NULL:
            raise MemoryError(f"Error creating linear operator {name}")

        cdef int error = add_edge(
            self.graph, from_node, to_node,
            op,
        )
        if error == 1:
            destroy_linear_operator(op)
        elif error == -4:
            raise Exception(f"A connection {from_node}->{to_node} already exists in the graph")
        elif error > 0:
            raise Exception(f"Error code {error} adding edge {from_node}->{to_node}")

    def remove_edge(self, from_node, to_node):
        """Remove an edge from the graph.

        This method removes an edge from `from_node` to `to_node` in the graph.
        If the edge does not exist in the graph, or if an error occurs while removing
        the edge, an exception is raised.

        Linear operator names and IDs associated with this edge are not removed from the
        graph when an edge is removed. See `.operator_indices` for a mapping of operator
        names to operator IDs and `.indices_operator_names` for a mapping of operator
        IDs to operator names.


        Parameters
        ----------
        from_node : int
            The index of the node where the edge starts.
        to_node : int
            The index of the node where the edge ends.

        Raises
        ------
        Exception
            If the edge does not exist in the graph, or if an error occurs while
            removing the edge.

        """
        self._validate_node(from_node)
        self._validate_node(to_node)

        error = remove_edge(self.graph, from_node, to_node)

        if error != 0:
            raise Exception(f"Removing connection {from_node}->{to_node} had error {error}")

    def get_edge_operator_expression(self, from_node, to_node):
        """
        Retrieves the operator expression associated with an edge between two nodes.

        Parameters
        ----------
        from_node : Node
            The source node of the edge.
        to_node : Node
            The target node of the edge.

        Returns
        -------
        list
            A list representation of the operator expression.

        Example
        -------
        For an operator expression `4*(1+2+3)` this will return a list respresentation
        of `('*', 4, ('+', 1, 2, 3))`. See `expression_node_to_tuple_form` for more details.

        Raises
        ------
        Exception
            If the connection between the nodes does not exist in the graph.
        Exception
            If there is no linear operator at the edge.
        Exception
            If there is no expression at the edge.
        """
        self._validate_node(from_node)
        self._validate_node(to_node)
        cdef Edge* edge = NULL

        if not edge_exists(self.graph, from_node, to_node, &edge):
            raise Exception(f"Connection {from_node}->{to_node} does not exist in the graph")
        else:
            if edge.operator == NULL:
                raise Exception("No linear operator at this edge")
            if edge.operator.expr == NULL:
                raise Exception("No expression at this edge")
            expr = expression_node_to_tuple_form(edge.operator.expr, self.indices_operator_names)
            if type(expr) is not tuple:
                return (expr,)
            else:
                return expr

    @property
    def number_of_self_loops(self):
        """Get the number of self-loops in the graph.

        This property returns the total number of self-loops in the graph. A node is considered
        to have a self-loop if the corresponding entry in the `self_loop` array of the graph is
        greater than 0. The total number of self-loops is the sum of these entries.

        Returns
        -------
        int
            The total number of self-loops in the graph.

        """
        return np.sum(<int[:self.graph.num_nodes]>self.graph.self_loop)

    @property
    def nodes_with_self_loops(self):
        """Get the nodes in the graph that have self-loops.

        This property returns a tuple of indices of the nodes in the graph that have self-loops.
        A node is considered to have a self-loop if the corresponding entry in the `self_loop`
        array of the graph is greater than 0.

        Returns
        -------
        tuple of int
            The indices of the nodes in the graph that have self-loops.

        """
        return tuple(i for i, n in enumerate(<int[:self.graph.num_nodes]>self.graph.self_loop) if n > 0)

    @property
    def self_loop_edges(self):
        """
        Get the edges in the graph that are self-loops.

        This property returns a tuple of tuples, where each inner tuple represents an edge that is a self-loop.
        Each inner tuple contains two identical elements, which are the index of the node that has a self-loop.

        Returns
        -------
        tuple of tuple of int
            The edges in the graph that are self-loops. Each edge is represented as a tuple of two identical integers,
            which are the index of the node that has a self-loop.
        """
        return tuple((i, i) for i, n in enumerate(<int[:self.graph.num_nodes]>self.graph.self_loop) if n > 0)

    def has_self_loop(self, node):
        """Check if a node has a self-loop.

        This method checks if the specified node has a self-loop in the graph.

        Parameters
        ----------
        node : int
            The index of the node to check.

        Returns
        -------
        int
            1 if the node has a self-loop, 0 otherwise.

        """
        self._validate_node(node)
        return int(self.graph.self_loop[int(node)])

    def in_degree(self, node):
        """Get the in-degree of a node.

        This method returns the in-degree of the specified node in the graph. The in-degree of a node is the number
        of edges coming into the node.

        Parameters
        ----------
        node : int
            The index of the node to check.

        Returns
        -------
        int
            The in-degree of the node.

        """
        self._validate_node(node)
        return int(self.graph.input_degree[int(node)])

    def out_degree(self, node):
        """Get the out-degree of a node.

        This method returns the out-degree of the specified node in the graph. The out-degree of a node is the number
        of edges going out of the node.

        Parameters
        ----------
        node : int
            The index of the node to check.

        Returns
        -------
        int
            The out-degree of the node.

        """
        self._validate_node(node)
        return int(self.graph.output_degree[int(node)])

    def fix_node(self, int node, bint state):
        """Fix a node to a specific state. When True the node will not be reduced/removed from the graph.

        This method fixes the specified node to the given state in the graph. If the node index is not valid,
        an exception is raised.

        Parameters
        ----------
        node : int
            The index of the node to fix.
        state : bint
            The state to which the node should be fixed. This should be a boolean-like value (0 or 1).

        Raises
        ------
        Exception
            If the node index is not valid (i.e., if it is less than 0 or greater than the number of nodes in the graph).

        """
        self._validate_node(node)
        if node < 0 or node > self.graph.num_nodes:
            raise Exception(f"Node should be between 0 and {self.graph.num_nodes}")
        else:
            self.graph.fixed_node[node] = state

    def next_reducible_node(self, keep=None):
        """
        Keeps returning a node index if there is one that can be reduced. Returns
        None once there are none left
        """
        for i in range(self.number_of_nodes):
            if self.has_self_loop(i) or (keep is not None and i in keep):
                continue
            if self.in_degree(i) == 1 and self.out_degree(i) == 1:
                return i
            elif self.in_degree(i) >= 1 and self.out_degree(i) == 1:
                return i
            elif self.in_degree(i) == 1 and self.out_degree(i) >= 1:
                return i
            elif self.in_degree(i) >= 1 and self.out_degree(i) >= 1:
                return i

        return None

    def evaluation_nodes(self, ignore_self_loops=False):
        """Nodes that have both inputs and outputs in the graph. These nodes must
        be included in the M matrix to solve a Ma=b type system.

        Parameters
        ----------
        ignore_self_loops : bool, optional
            When true any self loops at a node are not included in the determination
            if this node is a source

        Returns
        -------
        nodes : Tuple
            node integer values
        """
        if ignore_self_loops:
            return tuple([
                _ for _ in range(self.number_of_nodes)
                if self.out_degree(_)-self.has_self_loop(_) > 0 and self.in_degree(_)-self.has_self_loop(_) > 0
            ])
        else:
            return tuple([
                _ for _ in range(self.number_of_nodes)
                if self.out_degree(_) > 0 and self.in_degree(_) > 0
            ])

    def source_nodes(self, ignore_self_loops=False):
        """Nodes which have no input edges

        Parameters
        ----------
        ignore_self_loops : bool, optional
            When true any self loops at a node are not included in the determination
            if this node is a source

        Returns
        -------
        nodes : Tuple
            node integer values
        """
        if ignore_self_loops:
            return tuple([
                _ for _ in range(self.number_of_nodes)
                if self.out_degree(_)-self.has_self_loop(_) > 0 and self.in_degree(_)-self.has_self_loop(_) == 0
            ])
        else:
            return tuple([
                _ for _ in range(self.number_of_nodes)
                if self.out_degree(_) > 0 and self.in_degree(_) == 0
            ])

    def sink_nodes(self, ignore_self_loops=False):
        """Nodes which have no output edges

        Parameters
        ----------
        ignore_self_loops : bool, optional
            When true any self loops at a node are not included in the determination
            if this node is a sink

        Returns
        -------
        nodes : Tuple
            node integer values
        """
        if not ignore_self_loops:
            return tuple([
                _ for _ in range(self.number_of_nodes)
                if self.out_degree(_)-self.has_self_loop(_) == 0 and self.in_degree(_)-self.has_self_loop(_) > 0
            ])
        else:
            return tuple([
                _ for _ in range(self.number_of_nodes)
                if self.out_degree(_) == 0 and self.in_degree(_) > 0
            ])

    def isolated_nodes(self):
        """Nodes which have no input or output edges

        Returns
        -------
        nodes : Tuple
            node integer values
        """
        return tuple(
            [
                _ for _ in range(self.number_of_nodes)
                if self.in_degree(_) == 0 and self.out_degree(_) == 0
            ]
        )

    def to_networkx(self, ignore_nodes=None):
        """Convert the graph to a NetworkX MultiDiGraph.

        This method converts the current graph to a NetworkX MultiDiGraph. If `ignore_nodes` is provided,
        any edges involving nodes in `ignore_nodes` are not included in the resulting MultiDiGraph.

        Parameters
        ----------
        ignore_nodes : iterable of int, optional
            An iterable of node indices to ignore. If provided, any edges involving these nodes are
            not included in the resulting MultiDiGraph. By default, no nodes are ignored.

        Returns
        -------
        networkx.MultiDiGraph
            The NetworkX MultiDiGraph representation of the current graph.

        """
        import networkx as nx

        G = nx.MultiDiGraph()
        for n in range(self.number_of_nodes):
            for i, o, in self.output_edges(n):
                if ignore_nodes is not None and (i in ignore_nodes or o in ignore_nodes):
                    continue
                else:
                    G.add_edge(i, o)
        return G

    def plot(
            self,
            graphviz_prog="neato",
            pos=None,
            node_labels=None,
            edge_labels=False,
            ignore_nodes=None,
            alpha_nodes=None,
            alpha="44",
            dpi=200,
            svg=False
        ):
        """
        Plot the operator graph using Graphviz.

        Parameters
        ----------
        graphviz_prog : str, optional
            The Graphviz program to use for layout. Default is 'neato', see PyGraphviz for mode layouts.
        pos : dict, optional
            A dictionary mapping node names to positions. Default is None.
        node_labels : dict, optional
            Replace node indices with text labels, default is off.
        edge_labels : bool, optional
            Label edges with operator expressions, default is False.
        ignore_nodes : list, optional
            A list of nodes indices to ignore. Default is an empty list.
        alpha_nodes : list, optional
            A list of node indices to apply alpha transparency to. Default is an empty list.
        alpha : str, optional
            The doubled hexadecial alpha value for transparency. Default is '44',
            opqaue is 'FF', fully transparent is '00'
        dpi : int, optional
            Specifies the expected number of pixels per inch on a display device.
            Default is '200'
        svg : bool, optional
            Whether to output the graph as SVG. Default is False.

        Returns
        -------
        dict
            A dictionary mapping node names to positions.
        """
        if alpha_nodes is None:
            alpha_nodes = []

        from networkx.drawing.nx_agraph import to_agraph
        from IPython.display import Image, display, SVG
        from finesse.env import is_interactive
        from PIL import Image as PIL_Image
        import tempfile
        import webbrowser

        G = self.to_networkx(ignore_nodes=ignore_nodes)
        G.graph["splines"]="true"
        G.graph["overlap"]="false"
        G.graph["node"]={"color":"black", "style":"filled", "fillcolor":"#CCCCCC",}
        G.graph["dpi"]=dpi

        for n in G.nodes:
            if pos is not None and n in pos:
                G.nodes[n]["pos"] = pos[n]
            if n in alpha_nodes:
                G.nodes[n]["fillcolor"] = "#CCCCCC"+alpha
                G.nodes[n]["color"] = "#000000"+alpha
                G.nodes[n]["fontcolor"] = "#000000"+alpha

            if node_labels is not None:
                G.nodes[n]["label"] = node_labels[n]

        for a, b, c in G.edges:
            G[a][b][c]["penwidth"]=2
            if edge_labels:
                G[a][b][c]["label"] = str(self.get_edge_operator_expression(a, b))
            if a in alpha_nodes or b in alpha_nodes:
                G[a][b][c]["color"] = "#000000"+alpha
            else:
                G[a][b][c]["color"] = "#000000"

        for n, n in self.self_loop_edges:

            if n in alpha_nodes:
                G[n][n][0]["color"]="#FF0000"+alpha
            else:
                G[n][n][0]["color"]="#FF0000"

        A = to_agraph(G)
        if pos is None:
            A.layout(graphviz_prog)
        else:
            A.layout()
        img_fmt = "svg" if svg else "png"

        if is_interactive():
            ipy_func = SVG if svg else Image
            display(ipy_func(A.draw(format=img_fmt)))
        else:
            # Need to keep the file, since the python process exits after launching
            # the browser (when opening svg files)
            with tempfile.NamedTemporaryFile(suffix="." + img_fmt, delete=False) as f:
                A.draw(format=img_fmt, path=f.name)
                if svg:
                    webbrowser.open_new(f"file://{f.name}")
                else:
                    PIL_Image.open(f.name).show()

        positions = {n:n.attr["pos"] for n in A.nodes()}
        return positions

    def find_forkless_paths(self):
        """Finds all paths between nodes which do not have any forks in.
        Forks are defined here as a node with an input or output degree == 1 -
        except for the first and last node. Only paths with more than one edge
        are returned.

        Returns
        -------
        list
            Each element will be a list of nodes defining the edges of the
            forkless paths
        """
        def traverse(self, start, visited, path, final_paths):
            if visited[start]:
                return path[:-1]

            visited[start] = True

            in_degree = self.in_degree(start)
            out_degree = self.out_degree(start)

            if out_degree == 1 and in_degree <= 1:
                # A single output so keep following it
                i, o = tuple(self.output_edges(start))[0]
                path.append(i)
                return traverse(self, o, visited, path, final_paths)

            elif out_degree > 1 or in_degree > 1:
                path.append(start)
                if len(path) > 2:
                    final_paths.append(path) # Save this path
                for i, o in self.output_edges(start):
                    # then start the process for each branch
                    path = [i]
                    traverse(self, o, visited, path, final_paths)
            else:
                path.append(start)
                if len(path) > 2:
                    final_paths.append(path)
                return path

        visited = np.zeros(self.number_of_nodes, dtype=bool)
        final_paths = []
        for source in self.source_nodes() + self.evaluation_nodes():
            path = []
            traverse(self, source, visited, path, final_paths)

        if not all(visited):
            raise Exception(f"Missed some nodes: {visited}")

        return final_paths

    def series_rule(self, node):
        """Apply the series reduction rule to a node in the graph.

        Parameters
        ----------
        node : int
            The index of the node.

        Returns
        -------
        Tuple[Tuple[int, int, int]]
            A tuple of tuples representing the edges that have been reduced.
            Each tuple contains the indices of the start, mid, and end nodes.

        Raises
        ------
        Exception
            If the graph is null or if an error occurs while applying the rule.
        """
        cdef int error = 0
        cdef int start, end

        if self.graph == NULL:
            raise Exception("Graph is null")

        error = apply_series_rule(self.graph, node, &start, &end)

        if error < 0:
            ex = Exception(f"Error code {error} applying series rule to {node}")
            ex.error_code = error
            raise ex

        return ((start, node, end), )

    def split_rule(self, node):
        """Apply the split reduction rule to a node in the graph.

        Parameters
        ----------
        node : int
            The index of the node.

        Returns
        -------
        Tuple[Tuple[int, int, int]]
            A tuple of tuples representing the edges that have been reduced.
            Each tuple contains the indices of the start, mid, and end nodes.

        Raises
        ------
        Exception
            If the graph is null or if an error occurs while applying the rule.
        """
        cdef int error = 0, size, start
        cdef int* end = NULL
        try:
            if self.graph == NULL:
                raise Exception("Graph is null")

            error = apply_split_rule(self.graph, node, &start,  &size, &end)

            if error < 0:
                ex = Exception(f"Error code {error} applying split rule to {node}")
                ex.error_code = error
                raise ex

            reductions = []
            for i in range(size):
                reductions.append((start, node, end[i]))

            return tuple(reductions)

        finally:
            if end != NULL:
                free(end)


    def sum_rule(self, node):
        """Apply the sum reduction rule to a node in the graph.

        Parameters
        ----------
        node : int
            The index of the node.

        Returns
        -------
        Tuple[Tuple[int, int, int]]
            A tuple of tuples representing the edges that have been reduced.
            Each tuple contains the indices of the start, mid, and end nodes.

        Raises
        ------
        Exception
            If the graph is null or if an error occurs while applying the rule.
        """
        cdef int error = 0, size, end
        cdef int* start = NULL
        try:
            if self.graph == NULL:
                raise Exception("Graph is null")

            error = apply_sum_rule(self.graph, node, &size, &start, &end)

            if error < 0:
                ex = Exception(f"Error code {error} applying sum rule to {node}")
                ex.error_code = error
                raise ex

            reductions = []
            for i in range(size):
                reductions.append((start[i], node, end))

            return tuple(reductions)

        finally:
            if start != NULL:
                free(start)

    def fan_rule(self, node):
        """Apply the fan reduction rule to a node in the graph.

        Parameters
        ----------
        node : int
            The index of the node.

        Returns
        -------
        Tuple[Tuple[int, int, int]]
            A tuple of tuples representing the edges that have been reduced.
            Each tuple contains the indices of the start, mid, and end nodes.

        Raises
        ------
        Exception
            If the graph is null or if an error occurs while applying the rule.
        """
        cdef int error = 0, size = 0
        cdef int* start = NULL
        cdef int* end = NULL
        cdef int i = 0

        try:
            if self.graph == NULL:
                raise Exception("Graph is null")

            error = apply_fan_rule(self.graph, node, &size, &start, &end)

            if error < 0:
                ex = Exception(f"Error code {error} applying fan rule to {node}")
                ex.error_code = error
                raise ex

            if start == NULL:
                raise MemoryError("Start is NULL")
            if end == NULL:
                raise MemoryError("End is NULL")

            reductions = []
            for i in range(size):
                reductions.append((start[i], node, end[i]))

            return tuple(reductions)

        finally:
            if start != NULL:
                free(start)
            if end != NULL:
                free(end)


    def reduce(self, keep=None, reductions=None):
        """
        Reduces the graph to as few evaluations nodes as possible. Evaluation nodes are
        those that must be solved for when solving a system such as Ma = b. All other
        nodes are then either sinks or sources. Sinks do not need to be included in M as
        evaluation and source nodes solutions can be simply propagated to them.

        Parameters
        ----------
        keep : [list|tuple], optional
            nodes that should not be reduced
        reductions : list, optional
            Optional list that will be filled with the reductions applied

        Returns
        -------
        Number of reductions applied
        """
        cdef int total_reductions = 0

        if keep is None:
            keep = []

        for node in keep:
            self._validate_node(node)

        node = self.next_reducible_node(keep)

        while node is not None:
            if self.in_degree(node) == 1 and self.out_degree(node) == 1:
                applications = self.series_rule(node)
            elif self.in_degree(node) == 1 and self.out_degree(node) > 1:
                applications = self.split_rule(node)
            elif self.in_degree(node) > 1 and self.out_degree(node) == 1:
                applications = self.sum_rule(node)
            elif self.in_degree(node) > 1 and self.out_degree(node) > 1:
                applications = self.fan_rule(node)
            else:
                raise Exception(f"Node {node} is not reducible but marked as it should be")

            total_reductions += len(applications)
            if reductions is not None:
                reductions.extend(applications)

            node = self.next_reducible_node(keep)

        return total_reductions

    def __dealloc__(self):
        destroy_graph(self.graph)
