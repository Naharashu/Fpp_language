#include <stdio.h>
#include "include/lexer.h"
#include "include/parser.h"

// Function to print the AST (simplified for demonstration)
void print_ast(AST_T* node, int depth) {
    if (!node) {
        for (int i = 0; i < depth; i++) printf("  "); // Indentation
        printf("NULL Node\n");
        return;
    }

    for (int i = 0; i < depth; i++) printf("  "); // Indentation

    switch (node->type) {
        case AST_VARIABLE_DEFINITION:
            printf("Variable Definition: %s = ", node->variable_definition_variable_name);
            print_ast(node->variable_definition_value, depth + 1);
            break;
        case AST_STRING:
            printf("String: \"%s\"\n", node->string_value);
            break;
        case AST_INT:
            printf("Number: %d\n", node->number_value);
            break;
        case AST_BOOL:
            printf("Boolean: %s\n", node->bool_value ? "true" : "false");
            break;
        case AST_VARIABLE:
            printf("Variable: %s\n", node->variable_name);
            break;
        case AST_COMPOUND:
            printf("Compound:\n");
            for (int i = 0; i < node->compound_size; i++) {
                print_ast(node->compound_value[i], depth + 1);
            }
            break;
        default:
            printf("Unknown or Unhandled AST Node\n");
    }
}

int main() {
    // Example input to test the parser
    char* input = "var x = 42; var y = \"hello\"; var z = true;";
    
    // Initialize lexer
    lexer_T* lexer = init_lexer(input);
    
    // Initialize parser
    parser_T* parser = init_parser(lexer);
    
    // Parse the input
    AST_T* root = parser_parse(parser);
    
    // Print the parsed AST
    printf("Parsed AST:\n");
    print_ast(root, 0);

    return 0;
}