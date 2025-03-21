#ifndef CORE_OPERATOR_H
#define CORE_OPERATOR_H

#include <stdbool.h>
#include <complex.h>
#include "list.h"
#include "nary_expression_tree.h"


/**
 * Structure representing a linear operation, or a sum of linear operations if
 * multiple are applied between the same nodes.
 *
 * Members
 * -------
 * next : LinearOperator*
 *     The next linear operator to apply after this one to chain together mutliple
 *     operations when reducing graphs
 * operation : ExpressionNode*
 *     Operator expression tree describing the linear operation
 */
typedef struct LinearOperator LinearOperator;

struct LinearOperator{
    ExpressionNode* expr;
};

/**
 * Structure describing an Edge in a graph.
 *
 * Members
 * -------
 * from_node : int
 *     Node index this edge starts from
 * to_node : int
 *     Node index this edge goes to
 * operator : LinearOperator*
 *     The linear operator associated with this edge
 * next : Edge*
 *     Pointer to the next Edge leaving the `from` node
 */
typedef struct Edge {
    int from_node;
    int to_node;
    LinearOperator *operator;
    struct Edge* next;
} Edge;

/**
 * Structure describing a Multigraph: a directional graph allowing multiple edges
 * between two nodes, or "parallel edges". Each edge is uniquely indentified by
 * the name of the linear operator associated with it.
 *
 * Members
 * -------
 * num_nodes : int
 *     Number of nodes in this graph
 * num_edges : int
 *     Number of edges in the graph
 * input_degree : int*
 *     Array of length `num_nodes` describing input degree of node
 * output_degree : int*
 *     Array of length `num_nodes` describing output degree of node
 * self_loop : int*
 *     Array of length `num_nodes`, 0 if no self loops at the node >0 if there are
 * fixed_node : bool*
 *     Array of length `num_nodes`, when true this node should not be removed
 *     in any reduction steps
 * otuput : Edge**
 *     A list of lists describing all edges in the graph. First index is of
 *     size `num_nodes`. Each `Edge` then points to the next edge leaving from
 *     a particular node using the `Edge.next` pointer.
 */
typedef struct {
    int num_nodes;
    int num_edges;
    int* input_degree;
    int* output_degree;
    int* self_loop;
    bool* fixed_node;
    Edge** output_edges;
    ListItem** input_edges;
} Graph;

/**
 * Structure representing a set of edges in a graph.
 *
 * Members
 * -------
 * edges : Edge*
 *     Pointer to the dynamically allocated array of Edge structures.
 * size : int
 *     Current number of edges in the set.
 * capacity : int
 *     Current capacity of the set (maximum number of edges it can hold without resizing).
 */
typedef struct {
    Edge* edges;
    int size;
    int capacity;
} EdgeSet;

void destroy_graph(Graph* graph);
Graph* create_graph(int num_nodes);
void print_graph(Graph* graph);
LinearOperator* create_linear_operator(int id);
void destroy_linear_operator(LinearOperator* operator);
int add_operator(LinearOperator *A, LinearOperator *B);

int add_edge(Graph* graph, int from, int to, LinearOperator *operator);
bool edge_exists(Graph* graph, int from, int to, Edge **edge);
int remove_edge(Graph* graph, int from, int to);
LinearOperator* get_edge_linear_operator(Graph* graph, int from, int to);
int apply_series_rule(Graph* graph, int node, int* start, int* end);
int apply_sum_rule(Graph* graph, int node, int* size, int** start, int* end);
int apply_split_rule(Graph* graph, int node, int* start, int* size, int** end);
int apply_fan_rule(Graph* graph, int node, int* size, int** start, int** end);

#endif
