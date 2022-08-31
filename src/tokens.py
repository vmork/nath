# Dont rename file to 'token.py' because thats a builtin module
from typing import Any

# so that you can do ie "from tokens import token_types as tt; tt.PLUS"
# instead of using raw strings like 'PLUS' everywhere
class TokenType():
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    LEFT_BRACKET = "LEFT_BRACKET"
    RIGHT_BRACKET = "RIGHT_BRACKET"
    LEFT_BRACE = "LEFT_BRACE"
    RIGHT_BRACE = "RIGHT_BRACE"
    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    SLASH = "SLASH"
    CARET = "CARET"
    EQUAL = "EQUAL"
    BANG = "BANG"
    LT = "LT"
    GT = "GT"
    PLUS_EQUAL = "PLUS_EQUAL"
    MINUS_EQUAL = "MINUS_EQUAL"
    ARROW = "ARROW"
    STAR_EQUAL = "STAR_EQUAL"
    SLASH_EQUAL = "SLASH_EQUAL"
    CARET_EQUAL = "CARET_EQUAL"
    EQUAL_EQUAL = "EQUAL_EQUAL"
    BANG_EQUAL = "BANG_EQUAL"
    LT_EQUAL = "LT_EQUAL"
    GT_EQUAL = "GT_EQUAL"
    AND = "AND"
    OR = "OR"
    IF = "IF"
    ELSE = "ELSE"
    ELSEIF = "ELSEIF"
    TRUE = "TRUE"
    FALSE = "FALSE"
    FOR = "FOR"
    NULL = "NULL"
    PRINT = "PRINT"
    RETURN = "RETURN"
    IN = "IN"
    NOT = "NOT"
    EACH = "EACH"
    WHILE = "WHILE"
    OF = "OF"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    SEMICOLON = "SEMICOLON"
    COMMA = "COMMA"
    DOT_DOT = "DOT_DOT"
    RETURN = "RETURN"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    NEWLINE = "NEWLINE"
    EOF = "EOF"

tt = TokenType
lexeme_to_token = {
    "(": tt.LEFT_PAREN,
    ")": tt.RIGHT_PAREN,
    "[": tt.LEFT_BRACKET,
    "]": tt.RIGHT_BRACKET,
    "{": tt.LEFT_BRACE,
    "}": tt.RIGHT_BRACE,
    "+": tt.PLUS,
    "-": tt.MINUS,
    "*": tt.STAR,
    '^': tt.CARET,
    "/": tt.SLASH,
    "=": tt.EQUAL,
    "!": tt.BANG,
    "<": tt.LT,
    ">": tt.GT,
    "+=": tt.PLUS_EQUAL,
    "-=": tt.MINUS_EQUAL,
    "->": tt.ARROW,
    "*=": tt.STAR_EQUAL,
    "^=": tt.CARET_EQUAL,
    "/=": tt.SLASH_EQUAL,
    "==": tt.EQUAL_EQUAL,
    "!=": tt.BANG_EQUAL,
    "<=": tt.LT_EQUAL,
    ">=": tt.GT_EQUAL,
    "and": tt.AND,
    "or": tt.OR,
    "if": tt.IF,
    "else": tt.ELSE,
    "elseif": tt.ELSEIF,
    "true": tt.TRUE,
    "false": tt.FALSE,
    "for": tt.FOR,
    "null": tt.NULL,
    "print": tt.PRINT,
    "return": tt.RETURN,
    "in": tt.IN,
    "not": tt.NOT,
    "each": tt.EACH,
    "while": tt.WHILE,
    "of": tt.OF,
    "return": tt.RETURN,
    "break": tt.BREAK,
    "continue": tt.CONTINUE,
    ";": tt.SEMICOLON,
    ",": tt.COMMA,
    "..": tt.DOT_DOT,
    "\n": tt.NEWLINE,
    "\0": tt.EOF
}

class Token():
    def __init__(self, type: TokenType, lexeme: str=None, literal: Any=None, line_num: int=None):
        self.type: TokenType = type
        self.lexeme: str = lexeme
        self.literal: Any = literal
        self.line_num: int = line_num
    def istype(self, type) -> bool:
        return self.type == type
    def __repr__(self):
        return f"Token({self.type},{self.lexeme},{self.literal},{self.line_num})"
