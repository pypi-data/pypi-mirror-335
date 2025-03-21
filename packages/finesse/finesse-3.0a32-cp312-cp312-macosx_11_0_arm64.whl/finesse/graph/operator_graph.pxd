cdef extern from "list.h":
    ctypedef struct ListItem:
        void* ptr
        ListItem* next

cdef extern from "nary_expression_tree.h":
    ctypedef enum ExpressionNodeType:
        VALUE, ADD, MUL

    ctypedef struct Op:
        int allocd_operands
        int num_operands
        ExpressionNode **operands

    ctypedef union Data:
        int value
        Op op

    ctypedef struct ExpressionNode:
        ExpressionNodeType type
        size_t ref_count
        Data data

    cdef int free_node(ExpressionNode*)
    cdef ExpressionNode* create_value_node(int value)
    cdef ExpressionNode* create_op_node(ExpressionNodeType type, int num_operands)
    cdef int add_operand(ExpressionNode* node, ExpressionNode* operand)


cdef extern from "core_operator_graph.h":
    ctypedef struct string:
        size_t length
        char* ptr

    ctypedef struct LinearOperator:
        ExpressionNode* expr

    ctypedef struct Graph:
        int num_nodes
        int num_edges
        int* input_degree
        int* output_degree
        int* self_loop
        bint* fixed_node
        Edge** output_edges
        ListItem** input_edges

    ctypedef struct Edge:
        int from_node
        int to_node
        LinearOperator *operator
        Edge* next

    cdef Graph* create_graph(int num_nodes)
    cdef void destroy_graph(Graph* graph)
    cdef int add_edge(Graph* graph, int src, int dest, LinearOperator* operator)
    cdef bint edge_exists(Graph* graph, int from_node, int to_node, Edge **edge)
    cdef int remove_edge(Graph* graph, int src, int dest)
    cdef void print_graph(Graph* graph)
    cdef LinearOperator* create_linear_operator(int id)
    cdef void destroy_linear_operator(LinearOperator* operator)
    cdef LinearOperator* get_edge_linear_operator(Graph* graph, int from_node, int to_node)

    cdef int apply_series_rule(Graph* graph, int node, int* start, int* end)
    cdef int apply_sum_rule(Graph* graph, int node, int* size, int** start, int* end)
    cdef int apply_split_rule(Graph* graph, int node, int* start, int* size, int** end)
    cdef int apply_fan_rule(Graph* graph, int node, int* start, int** size, int** end)

cdef class OperatorGraph:
    cdef:
        Graph *graph
        dict operator_indices
        dict indices_operator_names
