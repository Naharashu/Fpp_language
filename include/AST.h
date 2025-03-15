#ifndef AST_H
#define AST_H
#include <ctype.h>
#include <stdlib.h>

typedef struct AST_STRUCT
{
    enum {
        AST_VARIABLE_DEFINITION,
        AST_VARIABLE,
        AST_STRING,
        AST_FUNCTION_CALL,
        AST_COMPOUND
    } type;

    /* Змінна */
    char* variable_definition_variable_name;
    struct AST_STRUCT* variable_definition_value;


    char* variable_name;
    
    /* функція */

    char* function_call_name;
    struct AST_STRUCT** function_call_arguments;
    size_t function_call_arguments_size;

    /* рядок */

    char* string_value;

    /* компаунд */

    struct AST_STRUCT** compound_value;
    size_t compound_size;

} AST_T;

AST_T* init_ast(int type);

#endif