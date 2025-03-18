#include <stdio.h>
#include "include/lexer.h"

int main() {
    lexer_T* lexer = init_lexer("var name = true;\nfalse; 123; \"Hello\";");

    token_T* token = NULL;
    do {
        token = lexer_get_next_token(lexer);
        print_token(token);
    } while (token->type != TOKEN_EOF);

    return 0;
}