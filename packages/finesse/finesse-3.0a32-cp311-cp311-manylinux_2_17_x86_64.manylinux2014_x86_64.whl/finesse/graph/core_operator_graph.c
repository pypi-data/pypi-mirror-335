#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include "core_operator_graph.h"
#include <assert.h>
#include "list.h"


/**
 * Creates a new linear operator.
 *
 * Parameters
 * ----------
 * id : int
 *     The unique integer ID for this linear operator
 *
 * Returns
 * -------
 * LinearOperator*
 *     A new linear operator created from an existing memory address. NULL if an error
 *     occurs allocating memory or making the operator expression.
 */
LinearOperator* create_linear_operator(int id) {
    LinearOperator* operator = calloc(1, sizeof(LinearOperator));
    if(operator == NULL) return NULL;

    operator->expr = create_value_node(id);
    if(operator->expr == NULL) {
        free(operator);
        return NULL;
    } else {
        return operator;
    }
}

/**
 * Returns a deepcopy of a LinearOperator.
 *
 * Parameters
 * ----------
 * LinearOperator*
 *     Operator to copy
 *
 * Returns
 * -------
 * LinearOperator*
 *     Copy of the provided operator, NULL if input is NULL
 */
LinearOperator* copy_linear_operator(LinearOperator *original) {
    if(original == NULL) return NULL;

    LinearOperator* operator = (LinearOperator*) calloc(1, sizeof(LinearOperator));
    operator->expr = copy_node(original->expr);

    return operator;
}

int add_operator(LinearOperator *A, LinearOperator *B) {
    if(A == NULL) return -1;
    if(B == NULL) return -2;

    // Add B to A
    if (A->expr->type == ADD) {
        // A is already a sum so just add B to it
        add_operand(A->expr, copy_node(B->expr));
        return 0;
    } else {
        // A is not a sum so make it one
        ExpressionNode* new_node = create_op_node(ADD, 2);
        add_operand(new_node, A->expr);
        add_operand(new_node, copy_node(B->expr));
        A->expr = new_node;
        return 0;
    }
}

int rmul_operator(LinearOperator *A, LinearOperator *B) {
    if(A == NULL) return -1;
    if(B == NULL) return -2;
    int error;

    // right multiply a copy of B to A: A * copy(B)
    if (A->expr->type == MUL) {
        // A is already a product so just add B to it
        error = add_operand(A->expr, copy_node(B->expr));
        if(error) return -100+error;
        return 0;
    } else {
        // A is not a product so make it one
        ExpressionNode* new_node = create_op_node(MUL, 2);
        if(new_node == NULL) return -1;
        error = add_operand(new_node, A->expr);
        if(error) return -1000+error;
        error = add_operand(new_node, copy_node(B->expr));
        if(error) return -10000+error;
        A->expr = new_node;
        return 0;
    }
}

int lmul_operator(LinearOperator *A, LinearOperator *B) {
    if(A != NULL) return -1;
    if(B != NULL) return -2;
    int error;

    // left multiply a copy of B to A: copy(B) * A
    if (A->expr->type == MUL) {
        // A is already a product so just add B to it
        error = add_operand(A->expr, copy_node(B->expr));
        if(error) return -100+error;
        return 0;
    } else {
        // A is not a product so make it one
        ExpressionNode* new_node = create_op_node(MUL, 2);
        if(new_node == NULL) return -1;
        error = add_operand(new_node, copy_node(B->expr));
        if(error) return -1000+error;
        error = add_operand(new_node, A->expr);
        if(error) return -10000+error;
        A->expr = new_node;
        return 0;
    }
}

/**
 * Destroys a linear operator, freeing any allocated resources.
 *
 * Parameters
 * ----------
 * operator : LinearOperator*
 *     Pointer to the linear operator to be destroyed.
 */
void destroy_linear_operator(LinearOperator* operator) {
    if (operator) {
        if(operator->expr) free_node(operator->expr);
        free(operator);
    }
}

/**
 * Creates a new graph with the specified number of nodes.
 *
 * Parameters
 * ----------
 * num_nodes : int
 *     Number of nodes in the graph.
 *
 * Returns
 * -------
 * Graph*
 *     Pointer to the newly created graph structure. NULL if a memory allocation
 *     error occured
 */
Graph* create_graph(int num_nodes) {
    Graph* graph = calloc(1, sizeof(Graph));
    if (graph != NULL) {
        graph->num_nodes = num_nodes;
        graph->output_edges = calloc(num_nodes, sizeof(Edge*));
        if (graph->output_edges == NULL) {
            destroy_graph(graph);
            return NULL;
        }

        graph->input_edges = calloc(num_nodes, sizeof(ListItem*));
        if (graph->input_edges == NULL) {
            destroy_graph(graph);
            return NULL;
        }

        graph->input_degree = calloc(num_nodes, sizeof(int));
        if (graph->input_degree == NULL) {
            destroy_graph(graph);
            return NULL;
        }

        graph->output_degree = calloc(num_nodes, sizeof(int));
        if (graph->output_degree == NULL) {
            destroy_graph(graph);
            return NULL;
        }

        graph->self_loop = calloc(num_nodes, sizeof(int));
        if (graph->output_degree == NULL) {
            destroy_graph(graph);
            return NULL;
        }

        graph->fixed_node = calloc(num_nodes, sizeof(bool*));
        if (graph->fixed_node == NULL) {
            destroy_graph(graph);
            return NULL;
        }
    }
    return graph;
}

/**
 * Destroys a graph, freeing any allocated resources.
 *
 * Parameters
 * ----------
 * graph : Graph*
 *     Pointer to the graph structure to be destroyed.
 *
 * Returns
 * -------
 * None
 */
void destroy_graph(Graph* graph) {
    if (graph != NULL) {
        int i;
        if(graph->output_edges){
            for (i = 0; i < graph->num_nodes; i++) {
                Edge* current = graph->output_edges[i];
                while (current != NULL) {
                    Edge* next = current->next;
                    destroy_linear_operator(current->operator);
                    if(current) free(current);
                    current = next;
                }
            }
            free(graph->output_edges);
        }
        if(graph->input_edges) {
            for (i = 0; i < graph->num_nodes; i++) {
                ListItem* current = graph->input_edges[i];
                while (current != NULL) {
                    ListItem* next = current->next;
                    free(current);
                    current = next;
                }
            }
            free(graph->input_edges);
        }
        if(graph->input_degree) free(graph->input_degree);
        if(graph->output_degree) free(graph->output_degree);
        if(graph->self_loop) free(graph->self_loop);
        if(graph->fixed_node) free(graph->fixed_node);
        free(graph);
    }
}

/**
 * Check if an edge is in a graph
 *
 * Parameters
 * ----------
 * graph : Graph*
 *     Pointer to the graph structure to check
 * from : int
 *     Index of the starting node of the edge
 * to : int
 *     Index of the ending node of the edge
 * edge : Edge**
 *     Return pointer to edge if it exists, set to NULL if it does not. If
 *     provided edge pointer is NULL then nothing is set
 *
 * Returns
 * -------
 * bool
 *     true if this connection is in the graph
 */
bool edge_exists(Graph* graph, int from, int to, Edge **edge){
    assert(graph != NULL);
    assert(from >= 0 && from < graph->num_nodes);
    assert(to >= 0 && to < graph->num_nodes);

    Edge* current = graph->output_edges[from];
    assert(current != NULL);

    while (current != NULL) {
        if (current->to_node == to) {
            if (edge) *edge = current;
            return true;
        }
        current = current->next;
    }
    if (edge) *edge = NULL;
    return false;
}

/**
 * Return an edge in a graph
 *
 * Parameters
 * ----------
 * graph : Graph*
 *     Pointer to the graph structure to search
 * from : int
 *     Index of the starting node of the edge
 * to : int
 *     Index of the ending node of the edge
 *
 * Returns
 * -------
 * Edge*
 *     NULL if not found
 */
Edge* get_edge(Graph* graph, int from, int to){
    Edge* current = graph->output_edges[from];
    while (current != NULL) {
        if (current->to_node == to) {
            return current;
        }
        current = current->next;
    }
    return NULL;
}

/**
 * Adds an edge to the graph with the specified linear operator.
 *
 * Parameters
 * ----------
 * graph : Graph*
 *     Pointer to the graph structure.
 * from : int
 *     Index of the starting node of the edge.
 * to : int
 *     Index of the ending node of the edge.
 * operator : LinearOperator
 *     Linear operator associated with the edge.
 *
 * Returns
 * -------
 * int
 *     +1 for edge already existing so linear operator was added to it
 *        passed operator can be freed if no longer needed as contents was copied
 *      0 for success
 *     -1 if graph is NULL
 *     -22 if from or to < 0 or > num_nodes
 *     -3 Edge memory allocation error
 *     -4 Edge already exists
 *     -5 ListItem memory allocation error
 */
int add_edge(Graph* graph, int from, int to, LinearOperator *operator) {
    Edge* edge = NULL;

    if (graph == NULL) return -1;

    if (from >= 0 && from < graph->num_nodes && to >= 0 && to < graph->num_nodes) {

        if (edge_exists(graph, from, to, &edge)) {
            // Edge already exists so we add an extra operation to the linear operator
            // which makes it a sum
            add_operator(edge->operator, operator);
            return 1;
        } else {
            edge = calloc(1, sizeof(Edge));
            if (edge != NULL) {
                edge->to_node = to;
                edge->from_node = from;
                edge->operator = operator;
                edge->next = graph->output_edges[from];
                graph->output_edges[from] = edge;
                graph->output_degree[edge->from_node] += 1;
                graph->input_degree[edge->to_node] += 1;
                if(from == to) graph->self_loop[edge->from_node] += 1;
                graph->num_edges += 1;
                // keep some log about the input edges going
                // into each node
                ListItem *item = calloc(1, sizeof(ListItem));
                if (item == NULL) return -5;
                item->ptr = (void*) edge;
                item->next = graph->input_edges[to];
                graph->input_edges[to] = item;
                return 0;
            } else {
                return -3;
            }
        }
    } else {
        return -22;
    }
}

/**
 * Removes an edge from a graph.
 *
 * Parameters
 * ----------
 * graph : Graph*
 *     Pointer to the graph structure to remove the edge from
 * from : int
 *     Index of the starting node of the edge
 * to : int
 *     Index of the ending node of the edge
 *
 * Returns
 * -------
 * int
 *      Error code, 0 for success
 *
 * Error codes
 * -----------
 *  0 for success
 * -1 if graph is NULL
 * -2 Edge does not exist
 * -3 Did not remove edge from any input list
 * -4 if from or to < 0 or > num_nodes
 * -100-N See remove_from_list error codes for N
 */
int remove_edge(Graph* graph, int from, int to) {
    Edge *edge = NULL, *current = NULL, *prev = NULL;

    if (graph == NULL) return -1;

    if (from >= 0 && from < graph->num_nodes && to >= 0 && to < graph->num_nodes) {
        if (! edge_exists(graph, from, to, &edge)) return -2;

        if (edge != NULL) {
            // Loop over edges going from node and remove it from the list
            Edge* current = graph->output_edges[from];
            while (current != NULL) {
                if(current->to_node == to) { // found edge to remove
                    if(prev == NULL) { // first in the list
                        if(current->next == NULL) { // nothing comes after this
                            graph->output_edges[from] = NULL; // empty list
                            break;
                        } else { // something comes after
                            graph->output_edges[from] = current->next;
                            break;
                        }
                    } else { // potentially mid-list or at the end
                        if(current->next == NULL) { // end of list
                            prev->next = NULL;
                            break;
                        } else { // something comes after
                            prev->next = current->next;
                            break;
                        }
                    }
                }
                prev = current;
                current = current->next;
            }

            int removed = remove_from_list( // Remove input edge from the 'to' node
                &(graph->input_edges[edge->to_node]),
                (void*)edge
            );
            if(removed == 0) return -3;
            if(removed < 0) return -100-removed;

            graph->output_degree[edge->from_node] -= 1;
            graph->input_degree[edge->to_node] -= 1;
            if(from == to) graph->self_loop[edge->from_node] -= 1;
            graph->num_edges -= 1;

            // TODO check this doesn't break
            //destroy_linear_operator(edge->operator);
            free(edge);
            return 0;
        } else {
            return -3;
        }
    } else {
        return -4;
    }
}

/**
 * Retrieves the linear operator associated with a specific edge in the graph.
 *
 * Parameters
 * ----------
 * graph : Graph*
 *     Pointer to the graph structure.
 * from : int
 *     Index of the starting node of the edge.
 * to : int
 *     Index of the ending node of the edge.
 *
 * Returns
 * -------
 * LinearOperator*
 *     Pointer to the linear operator associated with the specified edge.
 *     Returns NULL if the edge does not exist.
 */
LinearOperator* get_edge_linear_operator(Graph* graph, int from, int to) {
    if (graph != NULL && from >= 0 && from < graph->num_nodes && to >= 0 && to < graph->num_nodes) {
        Edge* current = graph->output_edges[from];
        while (current != NULL) {
            if (current->to_node == to) {
                return current->operator;
            }
            current = current->next;
        }
    }
    return NULL;
}

/**
 * Prints an ASCII representation of the graph to stdout
 *
 * Parameters
 * ----------
 * graph : Graph*
 *     Pointer to graph to print
 */
void print_graph(Graph* graph) {
    if (graph != NULL) {
        int i;
        for (i = 0; i < graph->num_nodes; i++) {
            Edge* current = graph->output_edges[i];
            if(current){
                printf("Node %d: ", i);
                while (current != NULL) {
                    printf("(%d) ", current->to_node);
                    current = current->next;
                }
                printf("\n");
            }
        }
    }
}

/**
 * Creates and initializes a new EdgeSet structure.
 *
 * Returns
 * -------
 * EdgeSet*
 *     Pointer to the newly created EdgeSet structure.
 *     Returns NULL if memory allocation fails.
 *     The caller is responsible for freeing the allocated memory.
 */
EdgeSet* create_edge_set() {
    EdgeSet* set = (EdgeSet*)calloc(1, sizeof(EdgeSet));
    if (set != NULL) {
        set->edges = NULL;
        set->size = 0;
        set->capacity = 0;
    }
    return set;
}

/**
 * Adds an edge to the EdgeSet.
 *
 * Parameters
 * ----------
 * set : EdgeSet*
 *     Pointer to the EdgeSet structure.
 *     The set must be previously created and initialized.
 * from : int
 *     Index of the starting node of the edge.
 * to : int
 *     Index of the ending node of the edge.
 *
 * Returns
 * -------
 * bool
 *     true if the edge is successfully added to the set, false otherwise.
 */
bool add_edge_to_set(EdgeSet* set, int from, int to) {
    // Check if the set is already full
    if (set->size >= set->capacity) {
        return false;
    }

    // Add the edge to the set
    Edge edge;
    edge.from_node = from;
    edge.to_node = to;
    set->edges[set->size++] = edge;

    return true;
}

/**
 * Checks if the EdgeSet is empty.
 *
 * Parameters
 * ----------
 * set : EdgeSet*
 *     Pointer to the EdgeSet structure.
 *     The set must be previously created and initialized.
 *
 * Returns
 * -------
 * bool
 *     true if the EdgeSet is empty, false otherwise.
 */
bool is_edge_set_empty(const EdgeSet* set) {
    return (set->size == 0);
}

/**
 * Removes the last added edge from the EdgeSet.
 *
 * Parameters
 * ----------
 * set : EdgeSet*
 *     Pointer to the EdgeSet structure.
 *     The set must be previously created and initialized.
 */
void remove_last_edge_from_set(EdgeSet* set) {
    if (!is_edge_set_empty(set)) {
        set->size--;
    }
}

/**
 * Recursively finds all simple paths between a current node and a target node in a directed graph using depth-first search (DFS).
 *
 * Parameters
 * ----------
 * graph : Graph*
 *     Pointer to the Graph structure representing the directed graph.
 *     The graph must be previously created and initialized.
 * current : int
 *     Index of the current node in the DFS traversal.
 * target : int
 *     Index of the target node for finding paths.
 * visited : bool[]
 *     Array of boolean values indicating the visited status of each node in the graph.
 *     The array must be of size graph->num_nodes and initialized to false before calling the function.
 * path_edges : EdgeSet*
 *     Pointer to the EdgeSet structure to store the edges along the paths.
 *     The structure must be previously created and initialized.
 *
 * Notes
 * -----
 * This function recursively performs a depth-first search (DFS) to find all possible simple paths
 * between the current node and the target node in the directed graph. The algorithm maintains a
 * boolean array to track the visited status of each node. It starts with the current node and marks
 * it as visited. It then explores all outgoing edges from the current node. If an edge leads to the
 * target node, it is added to the path_edges structure. If not, the algorithm continues the DFS
 * traversal by recursively calling the function with the next unvisited node. The process is repeated
 * until the target node is reached or all possible paths have been explored. The algorithm avoids
 * revisiting nodes that have already been visited in the same path to prevent cycles.
 *
 * The function modifies the path_edges structure, adding edges to it along the paths from the current
 * node to the target node. The caller is responsible for initializing the visited array to false before
 * calling the function and freeing the allocated memory for the path_edges structure when it's no longer
 * needed.
 */
void dfs_path_edges(Graph* graph, int current, int target, bool* visited, EdgeSet* path_edges) {
    visited[current] = true;

    if (current == target) {
        return;  // Reached the target node, stop the traversal
    }

    Edge* current_node = graph->output_edges[current];
    while (current_node != NULL) {
        int next = current_node->to_node;
        if (!visited[next]) {
            add_edge_to_set(path_edges, current, next);
            dfs_path_edges(graph, next, target, visited, path_edges);
            if (is_edge_set_empty(path_edges)) {
                remove_last_edge_from_set(path_edges);
            }
        }
        current_node = current_node->next;
    }
}

/**
 * Returns all the edges along a path between two nodes in the graph.
 *
 * Parameters
 * ----------
 * graph : Graph*
 *     Pointer to the graph structure.
 * start : int
 *     Index of the starting node of the path.
 * end : int
 *     Index of the ending node of the path.
 *
 * Returns
 * -------
 * EdgeSet*
 *     Pointer to the set of edges along the path.
 *     Returns NULL if the graph is NULL or the nodes are out of range.
 *     Returns an empty EdgeSet if no path exists between the nodes.
 *     The caller is responsible for freeing the allocated memory.
 */
EdgeSet* get_path_edges(Graph* graph, int start, int end) {
    if (graph != NULL && start >= 0 && start < graph->num_nodes && end >= 0 && end < graph->num_nodes) {
        // Create an empty EdgeSet to store the edges along the path
        EdgeSet* path_edges = create_edge_set();

        // Perform depth-first search to find the path
        bool* visited = (bool*)calloc(graph->num_nodes, sizeof(bool));
        dfs_path_edges(graph, start, end, visited, path_edges);

        // Free the memory allocated for the visited array
        free(visited);

        return path_edges;
    }
    return NULL;
}


/**
 * Appends the chain of operators in B to A. After this function call A will have
 * all operators applied in order.
 *
 * Parameters
 * ----------
 * LinearOperator*
 *     Operator to append operations to
 * LinearOperator*
 *     Operators to add
 *
 * Returns
 * -------
 * int
 *     0 on success, 1 on failure if A or B are NULL
 */
int append_operators(LinearOperator *A, LinearOperator *B) {
    return rmul_operator(A, B);
}

/**
 * Applies a series rule reduction to a node in a graph. This results in the node
 * becoming a sink node and the two operators A and B being applied directly from
 * nodes I->J. The node `N` must have only a single input and output edge for this
 * rule to be applied. Cannot apply rule to node if it has a self-loop.
 *
 * .. asciiart:
 *
 *     ┌───┐  A    ┌──────┐   B   ┌───┐      ┌───┐     BA      ┌───┐
 *     │ I ├──────►│ node ├──────►│ J │  ─►  │ I ├────────────►│ J │
 *     └───┘       └──────┘       └───┘      └─┬─┘             └───┘
 *                                             │    A    ┌──────┐
 *                                             └────────►│ node │
 *                                                       └──────┘
 * Parameters
 * ----------
 * graph : Graph*
 *     Pointer to the graph structure.
 * node : int
 *     Node to apply the series rule to.
 * start : int*
 *     Pointer to store the index of the starting node of the path (I).
 * end : int*
 *     Pointer to store the index of the ending node of the path (J).
 *
 * Returns
 * -------
 * error : int
 *    Error code, 0 for success
 *
 * Error Codes
 * -----------
 * -1
 *     The node index is out of range.
 * -2
 *     The node has a self-loop.
 * -3
 *     The node does not have exactly one input edge and one output edge.
 * -4
 *     The node's input edge is null.
 * -5
 *     The node's output edge is null.
 * -2000000000 + error
 *     An error occurred while appending the operators of the input and output edges.
 * -1000 + error
 *     An error occurred while adding an edge from the input edge's start node to the output edge's end node.
 * -1000000 + error
 *     An error occurred while removing the edge from the node to the output edge's end node.
 */
int apply_series_rule(Graph* graph, int node, int* start, int* end) {
    int error = 0;
    LinearOperator *new_op = NULL;

    if(node < 0 || node-1 >= graph->num_nodes) return -1;
    if(graph->self_loop[node] > 0) return -2;
    if(!(graph->input_degree[node] == 1 && graph->output_degree[node] == 1)) return -3;

    Edge* E1 = (Edge*) graph->input_edges[node]->ptr;
    if(E1 == NULL) return -4;
    Edge* E2 = graph->output_edges[node];
    if(E2 == NULL) return -5;

    *start = E1->from_node;
    *end = E2->to_node;

    new_op = copy_linear_operator(E1->operator);
    error = append_operators(new_op, copy_linear_operator(E2->operator));
    if(error) {
        return -2000000000 + error;
    }
    error = add_edge(graph, E1->from_node, E2->to_node, new_op);
    if(error == 1) {
        // edge already exists so the new operator was copied and added to it
        // so just free the operator we made.
        destroy_linear_operator(new_op);
    } else if(error) return -1000 + error;


    error = remove_edge(graph, node, E2->to_node);
    if(error) return -1000000 + error;
    return 0;
}


/**
 * Applies a sum rule reduction to a node in a graph. This results in the node
 * becoming a sink node and removable. The two operators A and B are applied with
 * C to two new edges I->K and J->K. The node `N` must have only a output but must
 * have >1 input edges for this rule to be applied. Cannot apply rule to node if
 * it has a self-loop.
 *
 * .. asciiart:
 *
 *     ┌───┐ A                          ┌───┐ CA
 *     │ I ├───┐                        │ I ├────┐
 *     └───┘   │  ┌──────┐ C  ┌───┐     └───┘    │    ┌───┐
 *             ├─►│ node ├───►│ K │ ──►          ├───►│ K │
 *     ┌───┐ B │  └──────┘    └───┘     ┌───┐ CB │    └───┘
 *     │ J ├───┘                        │ J ├────┘
 *     └───┘                            └───┘
 *
 * Parameters
 * ----------
 * graph : Graph*
 *     Pointer to the graph structure.
 * node : int
 *     Index of the node in the graph.
 * size : int*
 *     size of start array
 * start : int**
 *     Returned to the start nodes of the new edges. This must be freed once data
 *     is no longer needed.
 * end : int*
 *     Pointer to the end node of the new edges.
 *
 * Returns
 * -------
 * int
 *     0 if the operation is successful; a negative integer error code otherwise.
 *
 * Error Codes
 * -----------
 * -1
 *     The size pointer is null.
 * -2
 *     The start pointer is null.
 * -3
 *     The end pointer is null.
 * -4
 *     The node index is out of range.
 * -5
 *     The node has a self-loop.
 * -6
 *     The node does not have exactly one output edge and more than one input edge.
 * -7
 *     The node's output edge is null.
 * -8
 *     The node's input edge is null or an error occurred while appending the operators of the input and output edges.
 * -9
 *     An error occurred while copying and appending the operators.
 * -1000 + error
 *     An error occurred while adding an edge from the input edge's start node to the output edge's end node.
 * -1000000 + error
 *     An error occurred while removing the edge from the node to the output edge's end node.
 */
int apply_sum_rule(Graph* graph, int node, int* size, int** start, int* end) {
    int error = 0, i=0;
    LinearOperator *new_op = NULL, *next = NULL;
    ListItem *current = NULL;

    if(size == NULL) return -1;
    if(start == NULL) return -2;
    if(end == NULL) return -3;

    if(node < 0 || node-1 >= graph->num_nodes) return -4;
    if(graph->self_loop[node] > 0) return -5;
    if(!(graph->input_degree[node] >= 1 && graph->output_degree[node] == 1)) return -6;

    Edge* E2 = graph->output_edges[node];
    if(E2 == NULL) return -7;

    current = graph->input_edges[node];
    if(current == NULL) return -8;
    Edge* E1 = NULL;

    *size = graph->input_degree[node];
    *start = calloc(*size, sizeof(int));
    *end = E2->to_node;

    while(current != NULL) {
        E1 = (Edge*) current->ptr;
        if(E1 == NULL) return -8;

        new_op = copy_linear_operator(E1->operator);
        if(append_operators(new_op, copy_linear_operator(E2->operator))) {
            return -9;
        }
        error = add_edge(graph, E1->from_node, E2->to_node, new_op);
        if(error == 1) {
            // edge already exists so the new operator was copied and added to it
            // so just free the operator we made.
            destroy_linear_operator(new_op);
        } else if(error) return -1000 + error;

        (*start)[i++] = E1->from_node;

        current = current->next;
    }
    error = remove_edge(graph, node, E2->to_node);
    if(error) return -1000000 + error;


    return 0;
}


/**
 * Applies a split rule reduction to a node in a graph. This results in the node
 * becoming a sink node and removable. The operator A is applied with B and C and
 * creates two new edges I->J and I->K. The node `N` must have a single input
 * but multiple output nodes can be present. Cannot apply rule to node if it has
 * a self-loop.
 *
 * .. asciiart:
 *
 *                        B ┌───┐              BA ┌───┐
 *                       ┌─►│ J │            ┌───►│ J │
 *     ┌───┐ A  ┌──────┐ │  └───┘     ┌───┐  │    └───┘
 *     │ I ├───►│ node ├─┤        ──► │ I ├──┤
 *     └───┘    └──────┘ │C ┌───┐     └───┘  │ CA ┌───┐
 *                       └─►│ K │            └───►│ K │
 *                          └───┘                 └───┘
 *
 * Parameters
 * ----------
 * graph : Graph*
 *     Pointer to the graph structure.
 * node : int
 *     Index of the node in the graph.
 * start : int*
 *     Returned start node of the removed edges.
 * size : int*
 *     Returned size of the end array
 * end : int**
 *     Returned end nodes of the removed edges. This must be freed once data
 *     is no longer needed.
 *
 * Returns
 * -------
 * int
 *     0 if the operation is successful; a negative integer error code otherwise.
 *
 * Error Codes
 * -----------
 * -1
 *     The size pointer is null.
 * -2
 *     The start pointer is null.
 * -3
 *     The end pointer is null.
 * -4
 *     The node index is out of range.
 * -5
 *     The node has a self-loop.
 * -6
 *     The node does not have exactly one input edge and more than one output edge.
 * -7
 *     The node's input edge is null.
 * -8
 *     The node's output edge is null.
 * -9
 *     An error occurred while copying and appending the operators.
 * -1000 + error
 *     An error occurred while adding an edge from the input edge's start node to the output edge's end node.
 * -1000000 + error
 *     An error occurred while removing the edge from the node to the output edge's end node.
 */
int apply_split_rule(Graph* graph, int node, int* start, int* size, int** end) {
    int error = 0, i = 0;
    LinearOperator *new_op = NULL, *next = NULL;

    if(size == NULL) return -1;
    if(start == NULL) return -2;
    if(end == NULL) return -3;

    if(node < 0 || node-1 >= graph->num_nodes) return -4;
    if(graph->self_loop[node] > 0) return -5;
    if(!(graph->input_degree[node] == 1 && graph->output_degree[node] >= 1)) return -6;

    Edge* E1 = (Edge*)graph->input_edges[node]->ptr;
    if(E1 == NULL) return -7;

    Edge* E2 = graph->output_edges[node];
    if(E2 == NULL) return -8;

    *size = graph->output_degree[node];
    *end = calloc(*size, sizeof(int));
    *start = E1->from_node;

    while(E2 != NULL) {
        new_op = copy_linear_operator(E1->operator);
        if(append_operators(new_op, copy_linear_operator(E2->operator))) {
            return -9;
        }

        error = add_edge(graph, E1->from_node, E2->to_node, new_op);
        if(error == 1) {
            // edge already exists so the new operator was copied and added to it
            // so just free the operator we made.
            destroy_linear_operator(new_op);
        } else if(error) return -1000 + error;

        error = remove_edge(graph, node, E2->to_node);
        if(error) return -1000000 + error;

        (*end)[i++] = E2->to_node;

        E2 = E2->next;
    }

    return 0;
}


/**
 * Fan reduction rule is a generic form of the series and split rules. This takes
 * multiple input and output edges and distributes the incoming operators with the
 * output operators. The node in question ends up being made a sink node, it cannot
 * have a self loop.
 *
 * Parameters
 * ----------
 * graph : Graph*
 *     Pointer to the graph structure.
 * node : int
 *     Index of the node in the graph.
 * size : int*
 *     Size of the start and end arrays. Should be number of input x output edges.
 * start : int**
 *     Pointer to the start nodes of the reduced edges.
 * end : int**
 *     Pointer to the end nodes of the reduced edges.
 *
 * Returns
 * -------
 * int
 *     0 if the operation is successful; a negative integer error code otherwise.
 *
 * Error Codes
 * -----------
 * -2
 *     The size pointer is null.
 * -3
 *     The start pointer is null.
 * -4
 *     The end pointer is null.
 * -5
 *     The node index is out of range.
 * -6
 *     The node has a self-loop.
 * -7
 *     The node does not have at least one input edge and one output edge.
 * -8
 *     The node's input edge is null.
 * -9
 *     The node's output edge is null or an error occurred while appending the operators.
 * -1000 - error
 *     An error occurred while adding an edge from the input edge's start node to the output edge's end node.
 * -1000000 - error
 *     An error occurred while removing the edge from the node to the output edge's end node.
 */
int apply_fan_rule(Graph* graph, int node, int* size, int** start, int** end) {
    int error = 0, i = 0;
    LinearOperator *new_op = NULL, *next = NULL;
    ListItem *current = NULL;

    if(size == NULL) return -2;
    if(start == NULL) return -3;
    if(end == NULL) return -4;

    if(node < 0 || node-1 >= graph->num_nodes) return -5;
    if(graph->self_loop[node] > 0) return -6;
    if(!(graph->input_degree[node] >= 1 && graph->output_degree[node] >= 1)) return -7;

    *size = graph->input_degree[node] * graph->output_degree[node];
    *end = calloc(*size, sizeof(int));
    *start = calloc(*size, sizeof(int));

    current = graph->input_edges[node];
    // for each input edge, fan out the operator to the output edge node
    while(current != NULL){
        Edge *E1 = (Edge*) current->ptr;
        if(E1 == NULL) return -8;

        Edge* E2 = graph->output_edges[node];
        if(E2 == NULL) return -9;

        while(E2 != NULL) {
            new_op = copy_linear_operator(E1->operator);
            if(append_operators(new_op, copy_linear_operator(E2->operator))) {
                return -9;
            }
            error = add_edge(graph, E1->from_node, E2->to_node, new_op);
            if(error == 1) {
                // edge already exists so the new operator was copied and added to it
                // so just free the operator we made.
                destroy_linear_operator(new_op);
            } else if(error) return -1000 + error;

            (*start)[i] = E1->from_node;
            (*end)[i++] = E2->to_node;

            E2 = E2->next;
        }

        current = current->next;
    }

    // Finally, remove all output edges from the node
    Edge* E2 = graph->output_edges[node];
    if(E2 == NULL) return -10;

    while(E2 != NULL) {
        error = remove_edge(graph, node, E2->to_node);
        if(error) return -1000000 + error;
        E2 = E2->next;
    }

    return 0;
}
