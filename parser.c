#include "include/parser.h"
#include <stdio.h>
#include <string.h>

parser_T* init_parser(lexer_T* lexer) {
    parser_T* parser = calloc(1, sizeof(struct PARSER_STRUCT));
    parser->lexer = lexer;
    parser->current_token = lexer_get_next_token(lexer);
    parser->prev_token = parser->current_token;
    return parser;
}

void parser_eat(parser_T* parser, int token_type) {
    if (parser->current_token->type == token_type) {
        parser->prev_token = parser->current_token;
        parser->current_token = lexer_get_next_token(parser->lexer);
    } else {
        printf("Unexpected token `%d`, with type %d", parser->current_token->value, parser->current_token->type);
        exit(1);
    }
}

AST_T* parser_parse(parser_T* parser) {
    return parser_parse_statements(parser);
}

AST_T* parser_parse_statement(parser_T* parser) {
    switch (parser->current_token->type) {
        case TOKEN_ID: return parser_parse_id(parser);
    }
}

AST_T* parser_parse_statements(parser_T* parser) {
    AST_T* compound = init_ast(AST_COMPOUND);
    compound->compound_value = calloc(1, sizeof(struct AST_STRUCT*));
    AST_T* ast_statement = parser_parse_statement(parser);
    compound->compound_value[0] = ast_statement;
    compound->compound_size += 1;

    while (parser->current_token->type == TOKEN_SEMI) {
        parser_eat(parser, TOKEN_SEMI);
        AST_T* ast_statement = parser_parse_statement(parser);
        if (ast_statement) {
            compound->compound_size += 1;
            compound->compound_value = realloc(
                compound->compound_value,
                compound->compound_size * sizeof(struct AST_STRUCT*)
            );
            compound->compound_value[compound->compound_size-1] = ast_statement;
        }
    }
    return compound;
}

AST_T* parser_parse_expr(parser_T* parser) {
    AST_T* left = parser_parse_term(parser);
    while (parser->current_token->type == TOKEN_PLUS || parser->current_token->type == TOKEN_MINUS) {
        int operator_type = parser->current_token->type;
        parser_eat(parser, operator_type);
        AST_T* right = parser_parse_term(parser);
        AST_T* binary_op = init_ast(operator_type == TOKEN_PLUS ? AST_ADD : AST_SUB);
        binary_op->left = left;
        binary_op->right = right;
        left = binary_op;
    }

    switch (parser->current_token->type) {
        case TOKEN_INT: return parser_parse_number(parser);
        case TOKEN_ID: return parser_parse_id(parser);
        case TOKEN_STRING: return parser_parse_string(parser);
        case TOKEN_BOOL: return parser_parse_boolean(parser);
    }

    return left;
}

AST_T* parser_parse_factor(parser_T* parser) {
    if (parser->current_token->type == TOKEN_INT) {
        return parser_parse_number(parser);
    } else if (parser->current_token->type == TOKEN_ID) {
        return parser_parse_variable(parser);
    } else if (parser->current_token->type == TOKEN_LPAREN) {
        parser_eat(parser, TOKEN_LPAREN);
        AST_T* expr = parser_parse_expr(parser);
        parser_eat(parser, TOKEN_RPAREN);
        return expr;
    }
    return NULL;
}

AST_T* parser_parse_term(parser_T* parser) {
    AST_T* left = parser_parse_factor(parser);
    while (parser->current_token->type == TOKEN_MUL || parser->current_token->type == TOKEN_DIV) {
        int operator_type = parser->current_token->type;
        parser_eat(parser, operator_type);
        AST_T* right = parser_parse_factor(parser);
        AST_T* binary_op = init_ast(operator_type == TOKEN_MUL ? AST_MUL : AST_DIV);
        binary_op->left = left;
        binary_op->right = right;
        left = binary_op;
    }
    return left;
}

AST_T* parser_parse_function_call(parser_T* parser) {
    AST_T* function_call = init_ast(AST_FUNCTION_CALL);
    parser_eat(parser, TOKEN_LPAREN);
    function_call->function_call_name = parser->prev_token->value;
    function_call->function_call_arguments = calloc(1, sizeof(struct AST_STRUCT*));
    AST_T* ast_expr = parser_parse_expr(parser);
    function_call->function_call_arguments[0] = ast_expr;

    while (parser->current_token->type == TOKEN_COMMA) {
        parser_eat(parser, TOKEN_COMMA);
        AST_T* ast_expr = parser_parse_expr(parser);
        function_call->function_call_arguments_size += 1;
        function_call->function_call_arguments = realloc(function_call->compound_value, function_call->function_call_arguments_size * sizeof(struct AST_STRUCT));
        function_call->function_call_arguments[function_call->function_call_arguments_size-1] = ast_expr;
    }
    parser_eat(parser, TOKEN_RPAREN);
    return function_call;
}

AST_T* parser_parse_variable_definition(parser_T* parser) {
    parser_eat(parser, TOKEN_ID);
    char* variable_definition_variable_name = parser->current_token->value;
    parser_eat(parser, TOKEN_ID);
    parser_eat(parser, TOKEN_EQUALS);
    AST_T* variable_definition_value = parser_parse_expr(parser);
    AST_T* variable_definition = init_ast(AST_VARIABLE_DEFINITION);
    variable_definition->variable_definition_variable_name = variable_definition_variable_name;
    variable_definition->variable_definition_value = variable_definition_value;
    return variable_definition;
}

AST_T* parser_parse_variable(parser_T* parser) {
    char* token_value = parser->current_token->value;
    parser_eat(parser, TOKEN_ID);
    if (parser->current_token->type == TOKEN_LPAREN) {
        return parser_parse_function_call(parser);
    }
    AST_T* ast_variable = init_ast(AST_VARIABLE);
    ast_variable->variable_name = token_value;
    return ast_variable;
}

AST_T* parser_parse_string(parser_T* parser) {
    if (parser->current_token->type == TOKEN_STRING) {
        AST_T* ast_string = init_ast(AST_STRING);
        ast_string->string_value = strdup(parser->current_token->value); // Ensure string is copied
        parser_eat(parser, TOKEN_STRING);
        return ast_string;
    }
    return NULL;
}

AST_T* parser_parse_number(parser_T* parser) {
    if (parser->current_token->type == TOKEN_INT) {
        parser_eat(parser, TOKEN_INT);
        AST_T* ast_int = init_ast(AST_INT);
        ast_int->number_value = atoi(parser->prev_token->value);
        return ast_int;
    }
    return NULL;
}

AST_T* parser_parse_boolean(parser_T* parser) {
    if (strcmp(parser->current_token->value, "true") == 0 || strcmp(parser->current_token->value, "false") == 0) {
        AST_T* ast_bool = init_ast(AST_BOOL);
        ast_bool->bool_value = strcmp(parser->current_token->value, "true") == 0 ? 1 : 0;
        parser_eat(parser, TOKEN_BOOL);
        return ast_bool;
    }
    return NULL;
}

AST_T* parser_parse_id(parser_T* parser) {
    if (strcmp(parser->current_token->value, "var") == 0) {
        return parser_parse_variable_definition(parser);
    } else {
        return parser_parse_variable(parser);
    }
}