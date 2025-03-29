#######################################
# IMPORTS
#######################################

from strings_with_arrows import *

import string

import math

import sys

import random

import time

import gc

#######################################
# CONSTANTS
#######################################

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

#######################################
# ERRORS
#######################################

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        result  = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class ExpectedCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Expected character' , details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class RTError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'Runtime Error', details)
        self.context = context

    def as_string(self):
        result  = self.generate_traceback()
        result += f'{self.error_name}: {self.details}'
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx:
            result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        return 'Traceback (most recent call last):\n' + result

#######################################
# POSITION
#######################################

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if (current_char == '\n'):
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

#######################################
# TOKENS
#######################################

TT_INT                = 'INT'
TT_FLOAT        = 'FLOAT'
TT_STRING			= 'STRING'
TT_IDENTIFIER    = 'IDENTIFIER'
TT_KEYWORD        = 'KEYWORD'
TT_PLUS        = 'PLUS'
TT_MINUS        = 'MINUS'
TT_MUL        = 'MUL'
TT_DIV        = 'DIV'
TT_POW            = 'POW'
TT_EQ            = 'EQ'
TT_LPAREN        = 'LPAREN'
TT_RPAREN        = 'RPAREN'
TT_LBRACET       = 'LBRACET'
TT_RBRACET       = 'RBRACET'
TT_LSQUARE       = 'LSQUARE'
TT_RSQUARE       = 'RSQUARE'
TT_EE            = 'EE'
TT_NE            = 'NE'
TT_LT            = 'LT'
TT_GT            = 'GT'
TT_LTE        = 'LTE'
TT_GTE        = 'GTE'
TT_COMMA          = 'COMMMA'
TT_NEWLINE          = 'NEWLINE'
TT_ARROW          ='ARROW'
TT_TWODOT           = 'TWODOT'
TT_EOF            = 'EOF'

KEYWORDS = [
    'let',
    'and',
    'or',
    'not',
    'if',
    'elif',
    'else',
    'for',
    'to',
    'step',
    'while',
    'func',
    'add',
    'remove',
    'with',
    'get',
    'endf',
    'const',
    'int',
    'str',
    'bool',
    'arr'
]


class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end.copy()

    def matches(self, type_, value):
        return self.type == type_ and self.value == value
    
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'

#######################################
# LEXER
#######################################

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()
    
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in ';\n':
                tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            elif self.current_char == '"':
                tokens.append(self.make_string())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '^':
                tokens.append(Token(TT_POW, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == '[':
                tokens.append(Token(TT_LSQUARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == ']':
                tokens.append(Token(TT_RSQUARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA, pos_start=self.pos))
                self.advance()
            elif self.current_char == '{':
                tokens.append(Token(TT_LBRACET, pos_start=self.pos))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token(TT_RBRACET, pos_start=self.pos))
                self.advance()
            elif self.current_char == ':':
                tokens.append(Token(TT_TWODOT, pos_start=self.pos))
                self.advance()
            elif self.current_char == '!':
                token, error = self.make_not_equals()
                if error: 
                    return [], error
                tokens.append(token)
            elif self.current_char == '=':
                tokens.append(self.make_equals_or_arrow())
            elif self.current_char == '<':
                tokens.append(self.make_less_than())
                self.advance()
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
            num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

    def make_string(self):
        string = ''
        pos_start = self.pos.copy()
        escape_character = False
        self.advance()

        escape_characters = {
            'n': '\n',
            't': '\t'
        }

        while self.current_char != None and (self.current_char != '"' or escape_character):
            if escape_character:
                string += escape_characters.get(self.current_char, self.current_char)
                escape_character = False
            else:
                if self.current_char == '\\':
                    escape_character = True
                else:
                    string += self.current_char
            self.advance()

            escape_character = False
		
        self.advance()
        return Token(TT_STRING, string, pos_start, self.pos)

    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS + '_' + '.':
            id_str += self.current_char
            self.advance()

        tok_type = TT_KEYWORD if id_str.lower() in [k.lower() for k in KEYWORDS] else TT_IDENTIFIER
        return Token(tok_type, id_str.lower(), pos_start, self.pos)
    
    def make_equals_or_arrow(self):
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(TT_EE, pos_start=pos_start, pos_end=self.pos)
        elif self.current_char == '>':
            self.advance()
            return Token(TT_ARROW, pos_start=pos_start, pos_end=self.pos)
        return Token(TT_EQ, pos_start=pos_start, pos_end=self.pos)

    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None

        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!')")

    def make_equals(self):
        tok_type = TT_EQ
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_EE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_less_than(self):
        tok_type = TT_LT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_LTE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_greater_than(self):
        tok_type = TT_GT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_GTE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

#######################################
# NODES
#######################################

class StringNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'

class NumberNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'
    
class ListNode:
    def __init__(self, elementNodes, pos_start, pos_end):
        self.elementNodes = elementNodes
        
        self.pos_start = pos_start
        self.pos_end = pos_end

class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

class VarAssignNode:
    def __init__(self, var_name_tok, value_node, is_const=False, var_type=None):
        self.var_name_tok = var_name_tok
        self.value_node = value_node
        self.is_const = is_const
        self.var_type = var_type

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.value_node.pos_end

class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'
    
class ifNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        self.pos_start = cases[0][0].pos_start
        if self.else_case:
            node = self.else_case[0] if isinstance(self.else_case, tuple) else self.else_case
            self.pos_end = node.pos_end
        else:
            self.pos_end = self.cases[-1][1].pos_end

    def __repr__(self):
        return f'if: ({self.cases}, else: {self.else_case})'

    
class forNode:
    def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node, should_return_null=False):
        self.var_name_tok = var_name_tok
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node 
        self.step_value_node = step_value_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.body_node.pos_end

class whileNode:
    def __init__(self, condition_node, body_node, should_return_null=False):
        self.condition_node = condition_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end

class FuncDefNode:
    def __init__(self, var_name_tok, arg_names_toks, body_node):
        self.var_name_tok = var_name_tok
        self.arg_names_toks = arg_names_toks
        self.body_node = body_node

        if self.var_name_tok:
            self.pos_start = self.var_name_tok.pos_start
        elif len(self.arg_names_toks) > 0:
            self.pos_start = self.arg_names_toks[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end

class CallNode:
    def __init__(self, node_to_call, arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

        self.pos_start = self.node_to_call.pos_start
        if len(self.arg_nodes) > 0:
            self.pos_end = self.arg_nodes[len(self.arg_nodes)-1].pos_end
        else:
            self.pos_end = self.node_to_call.pos_end


###################################
# PARSE RESULT
#######################################

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advancement(self):
        self.advance_count += 1

    def register(self, res):
        self.advance_count += res.advance_count
        if res.error: self.error = res.error
        return res.node
    
    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advance_count == 0:
            self.error = error
        return self

#######################################
# PARSER
#######################################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self, ):
        self.tok_idx += 1
        self.update_current_tok()
        return self.current_tok
    
    def reverse(self, amount=1):
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok
    
    def update_current_tok(self):
        if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]

    def parse(self):
        res = self.statements()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '+', '-', '*', '/' or '^'"
            ))
        return res

    ###################################
    
    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()
        
        while self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()
            
        statement = res.register(self.expr())
        if res.error: return res
        statements.append(statement)
        
        more_statements = True
        
        while True:
            newline_count = 0
            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()
                newline_count += 1
            if newline_count == 0:
                more_statements = False
            if not more_statements:
                break
            statement = res.try_register(self.expr())
            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)
            
        return res.success(ListNode(
            statements,
            pos_start,
            self.current_tok.pos_end.copy()
        ))
    
    def comp_expr(self):
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD, 'not'):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, node))
        
        node = res.register(self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))

        if res.error:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected int, float, identifier, '+', '-', '(' or 'not' "))

        return res.success(node)
    
    def expr(self):
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD, 'if'):
                if_expr = res.register(self.if_expr())
                if res.error: return res
                return res.success(if_expr)

        if self.current_tok.matches(TT_KEYWORD, 'let') or self.current_tok.matches(TT_KEYWORD, 'const'):
            is_const = self.current_tok.matches(TT_KEYWORD, 'const')
            res.register_advancement()
            self.advance()
            
            var_type = None
            if self.current_tok.matches(TT_KEYWORD, 'int') or self.current_tok.matches(TT_KEYWORD, 'str') or self.current_tok.matches(TT_KEYWORD, 'bool') or self.current_tok.matches(TT_KEYWORD, 'arr'):
                var_type = self.current_tok.value
                res.register_advancement()
                self.advance()

            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected identifier"
                ))

            var_name = self.current_tok
            res.register_advancement()
            self.advance()


            if self.current_tok.type != TT_EQ:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '='"
                ))

            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            return res.success(VarAssignNode(var_name, expr, is_const, var_type))

        node = res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD, 'and'), (TT_KEYWORD, 'or'))))

        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'let', 'const','if', int, float, identifier, '+', '-', '(' or 'not'"
            ))

        return res.success(node)


    def power(self):
        return self.bin_op(self.call, (TT_POW, ), self.factor)

    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error: return res

        if self.current_tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            arg_nodes = []

            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ')', 'let', 'if', 'for', 'while', 'func', int, float, identifier, '+', '-', '(', '[' or 'not'"
                    ))

                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res

                if self.current_tok.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected ',' or ')'"
                    ))

                res.register_advancement()
                self.advance()
            return res.success(CallNode(atom, arg_nodes))
        return res.success(atom)

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def arith_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    
    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.type == TT_STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))

        elif tok.type == TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))

        elif tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))

        elif tok.type == TT_LSQUARE:
            list_expr = res.register(self.list_expr())
            if res.error: return res
            return res.success(list_expr)

        elif tok.matches(TT_KEYWORD, 'if'):
            if_expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(if_expr)

        elif tok.matches(TT_KEYWORD, 'for'):
            for_expr = res.register(self.for_expr())
            if res.error: return res
            return res.success(for_expr)

        elif tok.matches(TT_KEYWORD, 'while'):
            while_expr = res.register(self.while_expr())
            if res.error: return res
            return res.success(while_expr)

        elif tok.matches(TT_KEYWORD, 'func'):
            func_def = res.register(self.func_def())
            if res.error: return res
            return res.success(func_def)

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected int, float, identifier, string, 'let', 'while', 'for', 'if', '+', '-', '{', '[' or '('"
        ))

        
        

    ################################### 
    
    def list_expr(self):
        res = ParseResult()
        element_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type != TT_LSQUARE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected '['"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_RSQUARE:
            res.register_advancement()
            self.advance()
            return res.success(ListNode(element_nodes, pos_start, self.current_tok.pos_end.copy()))

        element_nodes.append(res.register(self.expr()))
        if res.error: return res

        while self.current_tok.type == TT_COMMA:
            res.register_advancement()
            self.advance()

            element_nodes.append(res.register(self.expr()))
            if res.error: return res

        if self.current_tok.type != TT_RSQUARE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected ',' or ']'"
            ))

        res.register_advancement()
        self.advance()
        return res.success(ListNode(element_nodes, pos_start, self.current_tok.pos_end.copy()))

    def if_expr(self):
        res = ParseResult()
        all_cases = res.register(self.if_expr_cases("if"))
        if res.error:
            return res
        cases, else_case = all_cases
        return res.success(ifNode(cases, else_case))

    def if_expr_b(self):
        return self.if_expr_cases("elif")

    def if_expr_c(self):
        res = ParseResult()
        else_case = None

        if self.current_tok.matches(TT_KEYWORD, "else"):
            res.register_advancement()
            self.advance()

            if self.current_tok.type == TT_LBRACET or self.current_tok.type == TT_NEWLINE:
                if self.current_tok.type == TT_LBRACET:
                    res.register_advancement()
                    self.advance()
                else:  # NEWLINE branch
                    res.register_advancement()
                    self.advance()
                statements = res.register(self.statements())
                if res.error: 
                    return res
                else_case = (statements, True)  
                if self.current_tok.type != TT_RBRACET:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end, "Expected '}'"
                    ))
                res.register_advancement()
                self.advance()
            else:
                # Otherwise, a single expression branch
                expr = res.register(self.expr())
                if res.error:
                    return res
                else_case = (expr, False)
        else:
            # If no "else" keyword, parse a single expression (or raise error)
            expr = res.register(self.expr())
            if res.error:
                return res
            else_case = (expr, False)
        return res.success(else_case)
    def if_expr_b_or_c(self):
        res = ParseResult()
        cases, else_case = [], None

        if self.current_tok.matches(TT_KEYWORD, "elif"):
            all_cases = res.register(self.if_expr_b())
            if res.error:
                return res
            cases, else_case = all_cases
        else:
            else_case = res.register(self.if_expr_c())
            if res.error:
                return res
            
        # Wrap the two values in a tuple (a single argument to success)
        return res.success((cases, else_case))

    def if_expr_cases(self, case_keyword):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(TT_KEYWORD, case_keyword):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, f"Expected '{case_keyword}'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if self.current_tok.type != TT_LBRACET:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected '{'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            statements = res.register(self.statements())
            if res.error: return res
            cases.append((condition, statements, True))  # true indicates the branch is a block

            if self.current_tok.type == TT_RBRACET:
                res.register_advancement()
                self.advance()
            else:
                all_cases = res.register(self.if_expr_b_or_c())
                if res.error: return res
                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:
            expr = res.register(self.expr())
            if res.error: return res
            cases.append((condition, expr, False))  # false indicates a single-expression branch
                
            if self.current_tok.type != TT_RBRACET:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected '}'"
                ))
            res.register_advancement()
            self.advance()

            all_cases = res.register(self.if_expr_b_or_c())
            if res.error: return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return res.success((cases, else_case))
        
    def for_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'for'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'for'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected identifier"
            ))

        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        # Check for equals sign
        if self.current_tok.type != TT_EQ:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '='"
            ))

        res.register_advancement()
        self.advance()
        
        # Parse start value
        start_value = res.register(self.expr())
        if res.error: return res

        # Check for 'to' keyword
        if not self.current_tok.matches(TT_KEYWORD, 'to'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'to'"
            ))

        res.register_advancement()
        self.advance()
        
        # Parse end value
        end_value = res.register(self.expr())
        if res.error: return res

        # Check for optional 'step' keyword
        if self.current_tok.matches(TT_KEYWORD, 'step'):
            res.register_advancement()
            self.advance()

            step_value = res.register(self.expr())
            if res.error: return res
        else:
            step_value = None

        # Look for opening curly brace (your syntax uses { } instead of THEN/END)
        if self.current_tok.type != TT_LBRACET:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '{'"
            ))

        res.register_advancement()
        self.advance()

        # Check if it's a block of statements or a single expression
        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error: return res

            if self.current_tok.type != TT_RBRACET:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '}'"
                ))

            res.register_advancement()
            self.advance()

            return res.success(forNode(var_name, start_value, end_value, step_value, body, True))
        else:
            # Single expression body
            body = res.register(self.expr())
            if res.error: return res

            if self.current_tok.type != TT_RBRACET:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '}'"
                ))

            res.register_advancement()
            self.advance()

            return res.success(forNode(var_name, start_value, end_value, step_value, body, False))

    def whileNode(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'while'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, f"Expected 'while'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if self.current_tok.type != TT_LBRACET:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, f"Expected '{{'"
                ))
        
        res.register_advancement()
        self.advance()

        body = res.register(self.expr())
        if res.error: return res

        if self.current_tok.type != TT_RBRACET:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, f"Expected '}}'"
                ))
        
        return res.success(whileNode(condition, body))
    
    def func_def(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'func'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, f"Expected 'func'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_IDENTIFIER:
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()
            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, f"Expected '('"
                ))
            
        else:
            var_name_tok = None
            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, f"Expected identifier or '('"
                ))
            
        res.register_advancement()
        self.advance()
        arg_name_toks = []

        if self.current_tok.type == TT_IDENTIFIER:
            arg_name_toks.append(self.current_tok)
            res.register_advancement()
            self.advance()

            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()

                if self.current_tok.type != TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected identifier"
                    ))

                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()

            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, f"Expected ',' or ')'"
                ))
            
        else:
            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, f"Expected identifier or ')'"
                ))
            
        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_ARROW:
            res.register_advancement()
            self.advance()
            node_to_return = res.register(self.expr())
            if res.error: return res

            return res.success(FuncDefNode(
                var_name_tok,
                arg_name_toks,
                node_to_return
            ))
            
        if self.current_tok.type != TT_TWODOT:
            return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, f"Expected ':'"
                ))
        
        res.register_advancement()
        self.advance()
        
        # Передача на багаторядковий варіант
        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()
            
            # Парсимо тіло функції як блок операторів
            body = res.register(self.statements())
            if res.error: return res
            
            # Перевіряємо наявність закриваючої дужки
            if self.current_tok.type != TT_RBRACET:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '}'"
                ))
            
            res.register_advancement()
            self.advance()
            
            # Повертаємо вузол функції
            return res.success(FuncDefNode(
                var_name_tok,
                arg_name_toks,
                body
            ))
        else:
            # Однорядковий варіант
            body = res.register(self.expr())
            if res.error: return res
            
            if self.current_tok.type != TT_RBRACET:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '}'"
                ))
            
            res.register_advancement()
            self.advance()
            
            return res.success(FuncDefNode(
                var_name_tok,
                arg_name_toks,
                body
            ))
            
        

    def bin_op(self, func_a, ops, func_b=None):
        if func_b == None:
            func_b = func_a
        
        res = ParseResult()
        left = res.register(func_a())
        if res.error: return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

    def while_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'while'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, f"Expected 'while'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if self.current_tok.type != TT_LBRACET:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, f"Expected '{{'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()
                        
            body = res.register(self.statements())
            if res.error: return res
                        
            if self.current_tok.type != TT_RBRACET:
                return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '}'"
                ))
            res.register_advancement()
            self.advance()
            
            return res.success(whileNode(condition, body, True))

        body = res.register(self.expr())
        if res.error: return res

        if self.current_tok.type != TT_RBRACET:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, f"Expected '}}'"
            ))

        res.register_advancement()
        self.advance()

        return res.success(whileNode(condition, body, False))

#######################################
# RUNTIME RESULT
#######################################

class RTResult:
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, res):
        if res.error: self.error = res.error
        return res.value

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self

#######################################
# VALUES
#######################################

class Value:
    def __init__(self):
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        return None, self.illegal_operation(other)

    def multed_by(self, other):
        return None, self.illegal_operation(other)

    def dived_by(self, other):
        return None, self.illegal_operation(other)

    def powed_by(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_ne(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lte(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gte(self, other):
        return None, self.illegal_operation(other)

    def anded_by(self, other):
        return None, self.illegal_operation(other)

    def ored_by(self, other):
        return None, self.illegal_operation(other)

    def notted(self):
        return None, self.illegal_operation(other)

    def execute(self, args):
        return RTResult().failure(self.illegal_operation())

    def copy(self):
        raise Exception('No copy method defined')

    def is_true(self):
        return False

    def illegal_operation(self, other=None):
        if not other:
            other = self
        return RTError(
            self.pos_start, other.pos_end,
            'Illegal operation',
            self.context
        )

class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def dived_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'Division by zero',
                    self.context
                )

            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def powed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_eq(self, other):
        if isinstance(other, Number):
            return Boolean(self.value == other.value).set_context(self.context), None
        elif isinstance(other, Boolean):
            return Boolean((1 if self.value else 0) == other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_ne(self, other):
        if isinstance(other, Number):
            return Boolean(self.value != other.value).set_context(self.context), None
        elif isinstance(other, Boolean):
            return Boolean((1 if self.value else 0) != other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Boolean(self.value < other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return Boolean(self.value > other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return Boolean(self.value <= other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return Boolean(self.value >= other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def anded_by(self, other):
        if isinstance(other, Number):
            return Boolean(self.value != 0 and other.value != 0).set_context(self.context), None
        elif isinstance(other, Boolean):
            return Boolean(self.value != 0 and other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def ored_by(self, other):
        if isinstance(other, Number):
            return Boolean(self.value != 0 or other.value != 0).set_context(self.context), None
        elif isinstance(other, Boolean):
            return Boolean(self.value != 0 or other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def notted(self):
        return Boolean(self.value == 0).set_context(self.context), None

    
    def __lt__(self, other):
        if isinstance(other, Number):
            return self.value < other.value
        return NotImplemented


    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != 0
    
    def __repr__(self):
        return str(self.value)

Number.null = Number(0)
Number.true = Number(1)
Number.false = Number(0)
Number.PI = Number(math.pi)
Number.E = Number(math.e)
     
class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
        
    def multed_by(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
        
    def get_comparison_eq(self, other):
        if isinstance(other, String):
            return Number(1 if self.value == other.value else 0).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_ne(self, other):
        if isinstance(other, String):
            return Number(1 if self.value != other.value else 0).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
        
    def is_true(self):
        return len(self.value) > 0
    
    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __str__(self):
        return self.value

    def __repr__(self):
        return f'"{self.value}"'
    
    
class Boolean(Value):
    def __init__(self, value):
        super().__init__()
        self.value = 1 if value else 0
        
    def added_to(self, other):
        return None, Value.illegal_operation(self, other)

    def subbed_by(self, other):
        return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        return None, Value.illegal_operation(self, other)

    def dived_by(self, other):
        return None, Value.illegal_operation(self, other)
    
    def powed_by(self, other):
        return None, Value.illegal_operation(self, other)

    def get_comparison_eq(self, other):
        if isinstance(other, Boolean):
            return Boolean(self.value == other.value).set_context(self.context), None
        elif isinstance(other, Number):
            return Boolean(self.value == (1 if other.value else 0)).set_context(self.context), None
        return None, Value.illegal_operation(self, other)
    
    def get_comparison_ne(self, other):
        if isinstance(other, Boolean):
            return Boolean(self.value != other.value).set_context(self.context), None
        elif isinstance(other, Number):
            return Boolean(self.value != (1 if other.value else 0)).set_context(self.context), None
        return None, Value.illegal_operation(self, other)

    def anded_by(self, other):
        if isinstance(other, Boolean):
            return Boolean(self.value and other.value).set_context(self.context), None
        elif isinstance(other, Number):
            return Boolean(self.value and other.value != 0).set_context(self.context), None
        return None, Value.illegal_operation(self, other)

    def ored_by(self, other):
        if isinstance(other, Boolean):
            return Boolean(self.value or other.value).set_context(self.context), None
        elif isinstance(other, Number):
            return Boolean(self.value or other.value != 0).set_context(self.context), None
        return None, Value.illegal_operation(self, other)

    def notted(self):
        return Boolean(not self.value).set_context(self.context), None

    def copy(self):
        copy = Boolean(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value == 1

    def __repr__(self):
        return "true" if self.value else "false"
    
Boolean.true = Boolean(True)
Boolean.false = Boolean(False)
    
class BaseFunction(Value):
    
    def __init__(self, name):
        super().__init__()
        self.name = name or "<lambda>"
        
    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context
    
    def check_args(self, arg_names, args):
        res = RTResult()
        if len(args) > len(arg_names):
            return res.failure(RTError(
                self.pos_start, self.pos_end,
                f"{len(args) - len(arg_names)} too many args passed into '{self.name}'",
                self.context
            ))

        if len(args) < len(arg_names):
            return res.failure(RTError(
                self.pos_start, self.pos_end,
                f"{len(arg_names) - len(args)} too few args passed into '{self.name}'",
                self.context
            ))
        return res.success(None)
    
    def populate_args(self, arg_names, args, exec_ctx):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arg_name, arg_value)
            
    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RTResult()
        res.register(self.check_args(arg_names, args))
        if res.error: return res
        self.populate_args(arg_names, args, exec_ctx)
        return res.success(None)

class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names

    def execute(self, args):
        res = RTResult()
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context()

        res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if res.error: return res

        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        if res.error: return res
        return res.success(value)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<function {self.name}>"
    
class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements
        
    def __len__(self):
        return len(self.elements)
    
    def __sum__(self):
        return sum(self.elements)
    
    def __reversed__(self):
        return reversed(self.elements)
        
    def added_to(self, other):
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None
    
    def __sort__(self):
        return sorted(self.elements)
    
    def subbed_by(self, other):
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return new_list, None
            except:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'Element in this index cannot be removed from list because index is out of range',
                    self.context
                )
        else:
            return None, Value.illegal_operation(self, other)
    
    def multed_by(self, other):
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, Value.illegal_operation(self, other)
        
    def dived_by(self, other):
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'Element in this index cannot be got from list because index is out of range',
                    self.context
                )
        else:
            return None, Value.illegal_operation(self, other)
        
    def __str__(self):
        return f'[{", ".join([str(x) for x in self.elements])}]'
    
    def __repr__(self):
        return f'{", ".join([str(x) for x in self.elements])}'

    def copy(self):
        copy = List(self.elements)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)
        
    def execute(self, args):
        res = RTResult()
        exec_ctx = self.generate_new_context()
        
        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)
        
        res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
        if res.error: return res
        
        return_value = res.register(method(exec_ctx))
        if res.error: return res
        return res.success(return_value)
        
    def no_visit_method(self, node, context):
        raise Exception(f'No execute_{self.name} method defined')
    
    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start,self.pos_end)
        return copy
    
    def __repr__(self):
        return f'<built-in function {self.name}>'
    
    ##############################################################
    
    def execute_write(self, exec_ctx):
        print(str(exec_ctx.symbol_table.get('value')))
        return RTResult().success(Number.null)
    execute_write.arg_names = ['value']  
    
    def execute_return_(self, exec_ctx):
        return RTResult().success(exec_ctx.symbol_table.get('value'))
    execute_return_.arg_names = ['value'] 
    
    def execute_tostr(self, exec_ctx):
        return RTResult().success(String(str(exec_ctx.symbol_table.get('value'))))
    execute_tostr.arg_names = ['value']  
    
    def execute_input(self, exec_ctx):
        text = input()
        return RTResult().success(String(text))
    execute_input.arg_names = []  
    
    def execute_inputn(self, exec_ctx):
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                print(f"'{text}' must be integer. Try again!")
        return RTResult().success(Number(number))
    execute_inputn.arg_names = [] 
    
    def execute_is_num(self, exec_ctx):
        is_num = isinstance(exec_ctx.symbol_table.get("value"), Number)
        return RTResult().success(Boolean(is_num))
    execute_is_num.arg_names = ['value']

    def execute_is_str(self, exec_ctx):
        is_str = isinstance(exec_ctx.symbol_table.get("value"), String)
        return RTResult().success(Boolean(is_str))
    execute_is_str.arg_names = ['value']

    def execute_is_array(self, exec_ctx):
        is_array = isinstance(exec_ctx.symbol_table.get("value"), List)
        return RTResult().success(Boolean(is_array))
    execute_is_array.arg_names = ['value']
    
    def execute_append(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        value = exec_ctx.symbol_table.get("value")
        
        if not isinstance(list_ , List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Firts argument must be a list",
                exec_ctx
            ))
            
        list_.elements.append(value)
        return RTResult().success(Number.null)
    execute_append.arg_names = ['list', 'value']
    
    def execute_pop(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        index = exec_ctx.symbol_table.get("index")
        
        if not isinstance(list_ , List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Firts argument must be a list",
                exec_ctx
            ))
            
        if not isinstance(index , Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be a number",
                exec_ctx
            ))    
            
        try:
            element = list_.elements.pop(index.value)
        except:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Element with this index could not be removed because index out of range!",
                exec_ctx
            ))
        return RTResult().success(element)
    execute_pop.arg_names = ['list', 'index']
    
    def execute_collect(self, exec_ctx):
        listA = exec_ctx.symbol_table.get("listA")
        listB = exec_ctx.symbol_table.get("listB")
        
        if not isinstance(listA , List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Firts argument must be a list",
                exec_ctx
            ))
            
        if not isinstance(listB , List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be a list",
                exec_ctx
            ))
            
        listA.elements.extend(listB.elements)
        return RTResult().success(Number.null)    
    execute_collect.arg_names = ["listA", "listB"]    
    
    def execute_unite(self, exec_ctx):
        listA = exec_ctx.symbol_table.get("listA")
        listB = exec_ctx.symbol_table.get("listB")
        
        if not isinstance(listA , List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Firts argument must be a list",
                exec_ctx
            ))
            
        if not isinstance(listB , List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be a list",
                exec_ctx
            ))
            
        listC = List(listA.elements + listB.elements)
        return RTResult().success(listC)    
    execute_unite.arg_names = ["listA", "listB"] 
    
    def execute_exit(self, exec_ctx):
        index = exec_ctx.symbol_table.get('index')
        if isinstance(index, Number):
            if index.value == 1:
                sys.exit(1)
            if index.value == 0:
                pass
            else:
                return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "This function accepts only 1 or 0!",
                exec_ctx
            ))
        else:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Index is not number",
                exec_ctx
            ))
        return RTResult().success(None)    
    execute_exit.arg_names = ['index']
    
    def execute_len(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list_")
        
        if not isinstance(list_ , List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be a list",
                exec_ctx
            ))
            
        return RTResult().success(Number(len(list_)))
            
    execute_len.arg_names = ['list_']
    
    def execute_sqrt(self, exec_ctx):
        num = exec_ctx.symbol_table.get("num")
        
        if not isinstance(num , Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be a num",
                exec_ctx
            ))
            
        return RTResult().success(Number(math.sqrt(num.value)))
            
    execute_sqrt.arg_names = ['num']
    
    def execute_abs(self, exec_ctx):
        num = exec_ctx.symbol_table.get("num")
        
        if not isinstance(num , Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be a num",
                exec_ctx
            ))
            
        return RTResult().success(Number(abs(num.value)))
            
    execute_abs.arg_names = ['num']
    
    def execute_round(self, exec_ctx):
        num = exec_ctx.symbol_table.get("num")
        
        if not isinstance(num , Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be a num",
                exec_ctx
            ))
            
        return RTResult().success(Number(round(num.value)))
            
    execute_round.arg_names = ['num']
    

    
    def execute_root(self, exec_ctx):
        num1 = exec_ctx.symbol_table.get("num1")
        num2 = exec_ctx.symbol_table.get("num2")
        
        if not isinstance(num1 , Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be a num",
                exec_ctx
            ))
            
        if not isinstance(num2 , Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be a num",
                exec_ctx
            ))
            
        return RTResult().success(Number(math.pow(num1.value, 1 / num2.value)))
            
    execute_root.arg_names = ['num1', 'num2']
    
    def execute_reverse(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list_")
        
        if not isinstance(list_ , List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be a list",
                exec_ctx
            ))
        rev_el = list(reversed(list_.elements))
        return RTResult().success(List(rev_el).set_context(exec_ctx).set_pos(self.pos_start, self.pos_end))
            
    execute_reverse.arg_names = ['list_']
    
    def execute_sum(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list_")
        
        if not isinstance(list_ , List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be a list",
                exec_ctx
            ))
        
        total = Number(0)
        for element in list_.elements:
            if not isinstance(element, Number):
                return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "All elements must be numbers",
                exec_ctx
            ))
            total, _ = total.added_to(element)
    
        return RTResult().success(total)
            
    execute_sum.arg_names = ['list_']
    
    def execute_type(self, exec_ctx):
        value = exec_ctx.symbol_table.get("value")
        value_ = "undefined"
        if isinstance(value, Number):
            value_ = "int"
        elif isinstance(value, String):
            value_ = "string"
        elif isinstance(value, Boolean):
            value_ = "bool"
        elif isinstance(value, List):
            value_ = "array"
        elif isinstance(value, Function):
            value_ = "function"
        else:
            value_ = "undefined"
        
        return RTResult().success(String(value_).set_context(exec_ctx).set_pos(self.pos_start, self.pos_end))
    execute_type.arg_names = ['value']
    
    def execute_sort(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list_")
        
        if not isinstance(list_ , List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be a list",
                exec_ctx
            ))
        sort_el = list(sorted(list_.elements))
        return RTResult().success(List(sort_el).set_context(exec_ctx).set_pos(self.pos_start, self.pos_end))
            
    execute_sort.arg_names = ['list_']
    
    def execute_sleep(self, exec_ctx):
        sec = exec_ctx.symbol_table.get("sec")
        
        if not isinstance(sec , Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be number (sleep works with seconds)",
                exec_ctx
            ))
        time.sleep(sec.value)
        return RTResult().success(Number.null)
    execute_sleep.arg_names = ['sec']
    
    def execute_random(self, exec_ctx):
        return RTResult().success(Number(random.random()))
    execute_random.arg_names = []
    
    def execute_random_num(self, exec_ctx):
        a = exec_ctx.symbol_table.get("a")
        b = exec_ctx.symbol_table.get("b")
        
        if not isinstance(a , Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be a num",
                exec_ctx
            ))
            
        if not isinstance(b , Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be a num",
                exec_ctx
            ))
        return RTResult().success(Number(random.randint(int(a.value), int(b.value))))
    execute_random_num.arg_names = ['a', 'b']
    

    
BuiltInFunction.write       = BuiltInFunction("write")
BuiltInFunction.return_     = BuiltInFunction("return_")
BuiltInFunction.tostr       = BuiltInFunction("tostr")
BuiltInFunction.input       = BuiltInFunction("input")
BuiltInFunction.inputn      = BuiltInFunction("inputn")
BuiltInFunction.is_num      = BuiltInFunction("is_num")
BuiltInFunction.is_str      = BuiltInFunction("is_str")
BuiltInFunction.is_array    = BuiltInFunction("is_array")
BuiltInFunction.append      = BuiltInFunction("append")
BuiltInFunction.pop         = BuiltInFunction("pop")
BuiltInFunction.collect     = BuiltInFunction("collect")
BuiltInFunction.unite       = BuiltInFunction("unite")
BuiltInFunction.exit        = BuiltInFunction("exit")
BuiltInFunction.len         = BuiltInFunction("len")
BuiltInFunction.sqrt        = BuiltInFunction("sqrt")
BuiltInFunction.reverse     = BuiltInFunction("reverse")
BuiltInFunction.root        = BuiltInFunction("root")
BuiltInFunction.abs         = BuiltInFunction("abs")
BuiltInFunction.round       = BuiltInFunction("round")
BuiltInFunction.sum         = BuiltInFunction("sum")
BuiltInFunction.type        = BuiltInFunction("type")
BuiltInFunction.sort        = BuiltInFunction("sort")
BuiltInFunction.random      = BuiltInFunction("random")
BuiltInFunction.sleep       = BuiltInFunction("sleep")
BuiltInFunction.random_num  = BuiltInFunction("random_num")

    
#######################################
# CONTEXT
#######################################

class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None

#######################################
# SYMBOL TABLE
#######################################

class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.constants = set()
        self.var_types = {}
        self.parent = parent

    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value, var_type=None):
        if name in self.constants:
            return False
        
        parent = self.parent
        while parent:
            if hasattr(parent, 'const') and name in parent.constants:
                return False
            parent = parent.parent
        
        self.symbols[name] = value
        if var_type:
            self.var_types[name] = var_type
        return True
    
    def set_constant(self, name, value, var_type=None):
        if name in self.symbols:
            return False
            
        self.symbols[name] = value
        self.constants.add(name)
        if var_type:
            self.var_types[name] = var_type
        return True
    
    def is_constant(self, name):
        if name in self.constants:
            return True
        
        parent = self.parent
        while parent:
            if hasattr(parent, 'const') and name in parent.constants:
                return True
            parent = parent.parent

        return False
    
    def get_type(self, name):
        if name in self.var_types:
            return self.var_types[name]
        parent = self.parent
        while parent:
            if hasattr(parent, 'var_types') and name in parent.var_types:
                return parent.var_types[name]
            parent = parent.parent
            
        return None

    def remove(self, name):
        if name in self.constants:
            self.constants.remove(name)
        del self.symbols[name]

#######################################
# INTERPRETER
#######################################

class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    ###################################

    def visit_NumberNode(self, node, context):
        return RTResult().success(
            Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_StringNode(self, node, context):
        return RTResult().success(
            String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
        
    def visit_ListNode(self, node, context):
        res = RTResult()
        elements = []

        for element_node in node.elementNodes:
            elements.append(res.register(self.visit(element_node, context)))
            if res.error: return res

        return res.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"'{var_name}' is not defined",
                context
            ))

        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.error: return res

        if node.var_type:
            if node.var_type == 'int':
                if not isinstance(value, Number) or isinstance(value.value, float):
                    return res.failure(RTError(
                        node.pos_start, node.pos_end,
                        f"Expected integer for variable '{var_name}'",
                        context
                    ))
            elif node.var_type == 'str':
                if not isinstance(value, String):
                    return res.failure(RTError(
                        node.pos_start, node.pos_end,
                        f"Expected string for variable '{var_name}'",
                        context
                    ))
            elif node.var_type == 'bool':
                if isinstance(value, Boolean):
                    pass
                elif not isinstance(value, Number) and value.value not in (0, 1):
                    value = Boolean(value.value == 1)
                else:
                    return res.failure(RTError(
                        node.pos_start, node.pos_end,
                        f"Expected boolean for variable '{var_name}'",
                        context
                    ))
            elif node.var_type == 'arr':
                if isinstance(value, List):
                    pass
                else:
                    return res.failure(RTError(node.pos_start, node.pos_end, f"Expected array for variable", context))

        if node.is_const:
            success = context.symbol_table.set_constant(var_name, value)
            if not success:
                return res.failure(RTError(
                    node.pos_start, node.pos_end,
                    f"Cannot change value of constant '{var_name}'",
                    context
                ))
        else:
            if context.symbol_table.is_constant(var_name):
                return res.failure(RTError(
                    node.pos_start, node.pos_end,
                    f"Cannot change value of constant '{var_name}'",
                    context
                ))
            context.symbol_table.set(var_name, value, node.var_type)
        return res.success(value)

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error: return res
        right = res.register(self.visit(node.right_node, context))
        if res.error: return res

        if node.op_tok.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == TT_MUL:
            result, error = left.multed_by(right)
        elif node.op_tok.type == TT_DIV:
            result, error = left.dived_by(right)
        elif node.op_tok.type == TT_POW:
            result, error = left.powed_by(right)
        elif node.op_tok.type == TT_EE:
            result, error = left.get_comparison_eq(right)
        elif node.op_tok.type == TT_NE:
            result, error = left.get_comparison_ne(right)
        elif node.op_tok.type == TT_LT:
            result, error = left.get_comparison_lt(right)
        elif node.op_tok.type == TT_GT:
            result, error = left.get_comparison_gt(right)
        elif node.op_tok.type == TT_LTE:
            result, error = left.get_comparison_lte(right)
        elif node.op_tok.type == TT_GTE:
            result, error = left.get_comparison_gte(right)
        elif node.op_tok.matches(TT_KEYWORD, 'and'):
            result, error = left.anded_by(right)
        elif node.op_tok.matches(TT_KEYWORD, 'or'):
            result, error = left.ored_by(right)

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res

        error = None

        if node.op_tok.type == TT_MINUS:
            number, error = number.multed_by(Number(-1))
        if node.op_tok.matches(TT_KEYWORD, 'not'):
            number, error = number.notted()

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))
        

    def visit_ifNode(self, node, context):
        res = RTResult()
        
        for condition, expr, is_block in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.error: 
                return res
            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.error: 
                    return res
                return res.success(expr_value)
        
        if node.else_case:
            else_expr, is_block = node.else_case
            else_value = res.register(self.visit(else_expr, context))
            if res.error: 
                return res
            return res.success(else_value)
        
        return res.success(Number(0))
    
    def visit_forNode(self, node, context):
        res = RTResult()
        elements = []

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.error: return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.error: return res

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.error: return res
        else:
            step_value = Number(1)

        i = start_value.value

        if step_value.value >= 0:
            condition = lambda: i <= end_value.value
        else:
            condition = lambda: i >= end_value.value
        
        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            body_result = res.register(self.visit(node.body_node, context))
            if res.error: return res
            

            if isinstance(body_result, List) and isinstance(node.body_node, ListNode):
                for item in body_result.elements:
                    elements.append(item) 
            else:
                elements.append(body_result)

            i += step_value.value


        return res.success(
            Number.null if node.should_return_null else
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_FuncDefNode(self, node, context):
        res = RTResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_names_toks]
        func_value = Function(func_name, body_node, arg_names).set_context(context).set_pos(node.pos_start, node.pos_end)

        if node.var_name_tok:
            context.symbol_table.set(func_name, func_value)

        return res.success(func_value)

    def visit_CallNode(self, node, context):
        res = RTResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.error: return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.error: return res

        if isinstance(value_to_call, List):
            method_name = node.node_to_call.var_name_tok.value
            if method_name == "add" and len(args) == 1:
                result, error = value_to_call.added_to(args[0])
            elif method_name == "remove" and len(args) == 1:
                result, error = value_to_call.remove(args[0])
            elif method_name == "with" and len(args) == 1:
                result, error = value_to_call.with_(args[0])
            elif method_name == "get" and len(args) == 1:
                result, error = value_to_call.get(args[0])
            else:
                return res.failure(RTError(
                    node.pos_start, node.pos_end,
                    f"Invalid method call or arguments for list: {method_name}",
                    context
                ))

            if error: return res.failure(error)
            return res.success(result)

        return_value = res.register(value_to_call.execute(args))
        if res.error: return res
        if return_value is None:
            return_value =Number.null
        return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(return_value)
    
    def visit_whileNode(self, node, context):
        res = RTResult()
        elements = []

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.error: return res
            
            if not condition.is_true(): break
            
            value = res.register(self.visit(node.body_node, context))
            if res.error: return res
            
            if isinstance(value, List) and isinstance(node.body_node, ListNode):
                for item in value.elements:
                    elements.append(item)
            else:
                elements.append(value)
        
        return res.success(
            Number.null if node.should_return_null else
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )


#######################################
# RUN
#######################################

global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number(0))
global_symbol_table.set("true", Boolean.true)
global_symbol_table.set("false", Boolean.false)
global_symbol_table.set("pi", Number.PI)
global_symbol_table.set("e", Number.E)
global_symbol_table.set("write", BuiltInFunction.write)
global_symbol_table.set("return", BuiltInFunction.return_)
global_symbol_table.set("tostr", BuiltInFunction.tostr)
global_symbol_table.set("input", BuiltInFunction.input)
global_symbol_table.set("inputn", BuiltInFunction.inputn)
global_symbol_table.set("isnum", BuiltInFunction.is_num)
global_symbol_table.set("isstr", BuiltInFunction.is_str)
global_symbol_table.set("isarray", BuiltInFunction.is_array)
global_symbol_table.set("append", BuiltInFunction.append)
global_symbol_table.set("pop", BuiltInFunction.pop)
global_symbol_table.set("collect", BuiltInFunction.collect)
global_symbol_table.set("unite", BuiltInFunction.unite)
global_symbol_table.set("exit", BuiltInFunction.exit)
global_symbol_table.set("len", BuiltInFunction.len)
global_symbol_table.set("sqrt", BuiltInFunction.sqrt)
global_symbol_table.set("reverse", BuiltInFunction.reverse)
global_symbol_table.set("root", BuiltInFunction.root)
global_symbol_table.set("abs", BuiltInFunction.abs)
global_symbol_table.set("round", BuiltInFunction.round)
global_symbol_table.set("sum", BuiltInFunction.sum)
global_symbol_table.set("type", BuiltInFunction.type)
global_symbol_table.set("sort", BuiltInFunction.sort)
global_symbol_table.set("random", BuiltInFunction.random)
global_symbol_table.set("random.num", BuiltInFunction.random_num)
global_symbol_table.set("sleep", BuiltInFunction.sleep)

def run(fn, text):
    # Generate tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error
    
    # Generate AST
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error

    # Run program
    interpreter = Interpreter()
    context = Context('<code>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)
    gc.enable()
    gc.collect()

    return result.value, result.error
