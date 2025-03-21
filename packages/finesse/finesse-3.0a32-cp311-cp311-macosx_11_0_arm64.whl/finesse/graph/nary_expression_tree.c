#include <stdlib.h>
#include <stdio.h>
#include "nary_expression_tree.h"

ExpressionNode* create_value_node(int value) {
    // printf("add %i\n", value);
    ExpressionNode* node = calloc(1, sizeof(ExpressionNode));
    node->type = VALUE;
    node->data.value = value;
    return node;
}

ExpressionNode* create_op_node(ExpressionNodeType type, int num_operands) {
    if(type != ADD && type != MUL) return NULL;
    // printf("add op %i %i\n", type, num_operands);
    ExpressionNode* node = calloc(1, sizeof(ExpressionNode));
    node->type = type;
    node->data.op.allocd_operands = num_operands;
    node->data.op.num_operands = 0;
    node->data.op.operands = calloc(num_operands, sizeof(ExpressionNode*));
    return node;
}

ExpressionNode* copy_node(ExpressionNode* node) {
    ExpressionNode* new_node = NULL;
    if (node == NULL) return NULL;

    if (node->type == VALUE) {
        new_node = create_value_node(node->data.value);
    } else {
        new_node = create_op_node(node->type, node->data.op.num_operands);
        for (int i = 0; i < node->data.op.num_operands; i++) {
            add_operand(new_node, copy_node(node->data.op.operands[i]));
        }
    }
    return new_node;
}

int expand_operands(ExpressionNode* node, int num_operands) {
    if (node == NULL) return -1;
    if (node->type == VALUE) return -2;
    if (num_operands <= node->data.op.allocd_operands) return 0;

    node->data.op.allocd_operands = num_operands;
    node->data.op.operands = realloc(node->data.op.operands, node->data.op.allocd_operands * sizeof(ExpressionNode*));
    if(node->data.op.operands == NULL) return -3;
    return 0;
}

int add_operand(ExpressionNode* node, ExpressionNode* operand) {
    if (node == NULL) return -1;
    if (operand == NULL) return -2;

    if (node->type == VALUE) {
        return -1; // Can't add an argument to a value node
    } else {
        // allocate more than required so we're not constantly reallocating
        if(node->data.op.num_operands >= node->data.op.allocd_operands){
            int result = expand_operands(node, node->data.op.num_operands + 2);
            if (result != 0) return -10+result;
        }
        node->data.op.operands[node->data.op.num_operands] = operand;
        node->data.op.num_operands++;
        // operand might be used many times in expressions so keep track of how many times it's used
        operand->ref_count++;
        return 0;
    }
}

int prepend_operand(ExpressionNode* node, ExpressionNode* operand) {
    if (node == NULL) return -1;
    if (operand == NULL) return -2;

    if (node->type == VALUE) {
        return -3; // Can't add an argument to a value node
    } else {
        // allocate more than required so we're not constantly reallocating
        if(node->data.op.num_operands >= node->data.op.allocd_operands){
            int result = expand_operands(node, node->data.op.num_operands + 2);
            if (result != 0) return -10+result;
        }
        // shift all the operands to the right in the array
        for (int i = node->data.op.num_operands; i > 0; i--) {
            node->data.op.operands[i] = node->data.op.operands[i-1];
        }
        node->data.op.operands[0] = operand;
        node->data.op.num_operands++;
        // operand might be used many times in expressions so keep track of how many times it's used
        operand->ref_count++;
        return 0;
    }

}

int free_node(ExpressionNode* node){
    ExpressionNode *curr = NULL;
    if (node == NULL) return -1;
    if (node->ref_count < 0) return -2;

    if (node->type == VALUE) {
        if (node->ref_count == 0) {
            //printf("rem %i\n", node->data.value);
            free(node);
        }
        return 0;
    } else {
        for (int i = 0; i < node->data.op.num_operands; i++) {
            curr = node->data.op.operands[i];
            curr->ref_count--;
            if (curr->ref_count == 0) {
                free_node(curr);
            }
        }
        if (node->ref_count == 0) {
            //printf("rem op %i %i\n", node->type, node->data.op.num_operands);
            free(node->data.op.operands);
            free(node);
        }
        return 0;
    }
}
