#include <stdio.h>
#include "include/lexer.h"
#include "include/parser.h"

int main() {
    lexer_T* lexer = init_lexer("var name = (\"Danilo\");\n");
    
    parser_T* parser = init_parser(lexer);
    AST_T* root = parser_parse(parser);

    printf("%d\n", root->type);

    return 0;
}