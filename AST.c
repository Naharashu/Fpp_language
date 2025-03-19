#include "include/AST.h"

AST_T* init_ast(int type) {
    AST_T* ast = calloc(1, sizeof(struct AST_STRUCT));
    ast->type = type;

   /* Змінна */
   ast->variable_definition_variable_name = (void*) 0;
   ast->variable_definition_value = (void*) 0;


   ast->variable_name = (void*) 0;
   
   /* функція */

   ast->function_call_name = (void*) 0;
   ast->function_call_arguments = (void*) 0;
   ast->function_call_arguments_size = 0;

   /* рядок */

   ast->string_value = (void*) 0;

    /* компаунд */

    ast->compound_value = (void*) 0;
    ast->compound_size = 0;


    /* число */

    ast->number_value = 0;

    /* булеве значення */

    ast->bool_value = 0;

    return ast;
}