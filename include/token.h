#ifndef TOKEN_H
#define TOKEN_H

typedef struct TOKEN_STRUCT {
	enum {
		TOKEN_ID,
		TOKEN_EQUALS,
		TOKEN_PLUS,
		TOKEN_MINUS,
		TOKEN_MUL,
		TOKEN_DIV,
		TOKEN_STRING,
		TOKEN_INT,
		TOKEN_BOOL,
		TOKEN_SEMI,
		TOKEN_LPAREN,
		TOKEN_RPAREN,
		TOKEN_LBRACE,
		TOKEN_RBRACE,
		TOKEN_COMMA,
		TOKEN_EOF
	} type;
	
	char* value;
} token_T;

token_T* init_token(int type, char* value);
#endif