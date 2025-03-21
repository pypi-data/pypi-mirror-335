#ifndef NARY_EXPRESSION_TREE_H
#define NARY_EXPRESSION_TREE_H

typedef enum { ADD, MUL, VALUE } ExpressionNodeType;

typedef struct ExpressionNode ExpressionNode;
struct ExpressionNode {
    ExpressionNodeType type;
    size_t ref_count;
    union {
        int value;  // If type is VALUE, this field is used
        struct {
            int allocd_operands;
            int num_operands;  // If type is ADD or MUL, these fields are used
            struct ExpressionNode **operands;
        } op;
    } data;
};

ExpressionNode* create_value_node(int value);
ExpressionNode* create_op_node(ExpressionNodeType type, int num_operands);
int add_operand(ExpressionNode* node, ExpressionNode* operand);
int free_node(ExpressionNode* node);
ExpressionNode* copy_node(ExpressionNode* node);

#endif // NARY_EXPRESSION_TREE_H
