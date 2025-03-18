#include "include/lexer.h"
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdio.h>

lexer_T* init_lexer(char* contents) {
	lexer_T* lexer =  calloc(1, sizeof(struct LEXER_STRUCT));
	lexer->contents = contents;
	lexer->i = 0;
	lexer->c = contents[lexer->i];

	return lexer;
}

void lexer_advance(lexer_T* lexer) {
	if (lexer->c != '\0' && lexer->i < strlen(lexer->contents)) {
		lexer->i += 1;
		lexer->c = lexer->contents[lexer->i];
	}
}

void lexer_skip_whitespace(lexer_T* lexer) {
	while (lexer->c == ' ' || lexer->c == 10) {
		lexer_advance(lexer);
	}
}

token_T* lexer_get_next_token(lexer_T* lexer) {
	while (lexer->c != '\0' && lexer->i < strlen(lexer->contents)) {
		if (lexer->c == ' ' || lexer->c == 10) {
			lexer_skip_whitespace(lexer);
		}

		if (isalnum(lexer->c)) {
			return lexer_collect_id(lexer);
		}

		if (isdigit(lexer->c)) {
			return lexer_collect_int(lexer);
		}
		if (lexer->c == '"') {
			return lexer_collect_string(lexer);
		}

		if (lexer->c == 'true' || lexer->c == 'false') {
			return lexer_collect_bool(lexer);
		}

		switch (lexer->c) {
			case '=': return lexer_advance_with_token(lexer, init_token(TOKEN_EQUALS, lexer_get_current_char_as_string(lexer))); break;
			case ';': return lexer_advance_with_token(lexer, init_token(TOKEN_SEMI, lexer_get_current_char_as_string(lexer))); break;
			case '(': return lexer_advance_with_token(lexer, init_token(TOKEN_LPAREN, lexer_get_current_char_as_string(lexer))); break;
			case ')': return lexer_advance_with_token(lexer, init_token(TOKEN_RPAREN, lexer_get_current_char_as_string(lexer))); break;
			case ',': return lexer_advance_with_token(lexer, init_token(TOKEN_COMMA, lexer_get_current_char_as_string(lexer))); break;
			case '{': return lexer_advance_with_token(lexer, init_token(TOKEN_LBRACE, lexer_get_current_char_as_string(lexer))); break;
			case '}': return lexer_advance_with_token(lexer, init_token(TOKEN_RBRACE, lexer_get_current_char_as_string(lexer))); break;
		}
	}

	return init_token(TOKEN_EOF, "\0");
}

token_T* lexer_collect_string(lexer_T* lexer) {
	lexer_advance(lexer);

	char* value = calloc(1, sizeof(char));
	value[0] = '\0';

	while (lexer->c != '"')
	{
		char* s = lexer_get_current_char_as_string(lexer);
		value = realloc(value, (strlen(value) + strlen(s) + 1) * sizeof(char));
		strcat(value, s);

		lexer_advance(lexer);
	}
	
	lexer_advance(lexer);

	return init_token(TOKEN_STRING, value);
}

token_T* lexer_collect_id(lexer_T* lexer) {


	char* value = calloc(1, sizeof(char));
	value[0] = '\0';

	while (isalnum(lexer->c) )
	{
		char* s = lexer_get_current_char_as_string(lexer);
		value = realloc(value, (strlen(value) + strlen(s) + 1) * sizeof(char));
		strcat(value, s);

		lexer_advance(lexer);
	}
	

	return init_token(TOKEN_ID, value);
}


token_T* lexer_collect_int(lexer_T* lexer) {
	char* value = calloc(1, sizeof(char));
	value[0] = '\0';

	while (isdigit(lexer->c)) {
		char* s = lexer_get_current_char_as_string(lexer);
		value = realloc(value, (strlen(value) + strlen(s) + 1) * sizeof(char));
		strcat(value, s);

		lexer_advance(lexer);
	}

	return init_token(TOKEN_INT, value);
}



token_T* lexer_advance_with_token(lexer_T* lexer, token_T* token) {
	lexer_advance(lexer);

	return token;
}

char* lexer_get_current_char_as_string(lexer_T* lexer) {
	char* str = calloc(2, sizeof(char));
	str[0] = lexer->c; 
	str[1] = '\0';
	
	return str;
}

token_T* lexer_collect_bool(lexer_T* lexer) {
    char* value = calloc(1, sizeof(char));
    value[0] = '\0';

    while (isalnum(lexer->c)) {
        char* s = lexer_get_current_char_as_string(lexer);
        value = realloc(value, (strlen(value) + strlen(s) + 1) * sizeof(char));
        strcat(value, s);

        lexer_advance(lexer);
    }

    if (strcmp(value, "true") == 0 || strcmp(value, "false") == 0) {
        return init_token(TOKEN_BOOL, value);
    }

    return init_token(TOKEN_ID, value);
}

void print_token(token_T* token) {
    printf("TOKEN(type=%d, value='%s')\n", token->type, token->value);
}



