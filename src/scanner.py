from src.errors import NathSyntaxError
from src.tokens import Token, TokenType as tt, lexeme_to_token

one_char_lexemes = ["(", ")", "[", "]", "{", "}", ";", ","]
one_or_two_char_lexemes = ["+", "-", "-", "*", "/", "=", "!", "<", ">", "^", "."]
keywords = ["and", "or", "if", "else", "elseif", "true", "false", "for", "null", 
    "print", "return", "in", "not", "each", "while", "of"]

class Scanner():
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1   

    def scan_tokens(self) -> list:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.add_token(tt.EOF, lexeme=None)
        return self.tokens
    
    def scan_token(self):
        c = self.advance()
        match c:
            # unambiguous one-char lexemes
            case c if c in one_char_lexemes:
                self.add_token(lexeme_to_token[c])

            # lexemes that are either one or two chars long
            case c if c in one_or_two_char_lexemes:
                two_char = c + self.peek()
                if two_char in lexeme_to_token:
                    self.advance()
                    self.add_token(lexeme_to_token[two_char])
                elif c in lexeme_to_token:
                    self.add_token(lexeme_to_token[c])
            
            # strings are always enclosed by " "
            case '"': self.handle_string()
            # numbers start with a digit and can have a decimal point
            case c if c.isdigit(): self.handle_number()
            # identifiers and keywords
            case c if c.isalpha() or c == "_": self.handle_identifier()
            # comments start with '#' and are ignored
            case "#": self.handle_comment()
            # ignore whitespace
            case " " | "\r" | "\t": pass
            case "\n": 
                self.add_token(tt.NEWLINE, lexeme=repr("\n"))
                self.line += 1

            case _:
                raise NathSyntaxError(self.line, f"Invalid character: {c}")
    
    def ignore_newlines(self):
        while self.peek() == '\n':
            self.line += 1
            self.advance()
    
    def handle_string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n': self.line += 1
            self.advance()
        if self.is_at_end():
            raise NathSyntaxError(self.line, "String was not closed")

        value = self.source[self.start+1:self.current]
        self.advance() # consume closing "
        self.add_token(tt.STRING, literal=value)
    
    def valid_digit(self, c):
        return c.isdigit() or c == '_'
    
    def handle_number(self):
        while self.valid_digit(self.peek()): 
            self.advance()
        if self.peek() in ['.', 'e'] and self.peek2().isdigit():
            self.advance() # consume decimal point or 'e'
            while self.valid_digit(self.peek()): self.advance()
        self.add_token(tt.NUMBER, literal=float(self.source[self.start:self.current]))

    def handle_identifier(self):
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()
        value = self.source[self.start:self.current]
        if value in keywords:
            self.add_token(lexeme_to_token[value])
        else: self.add_token(tt.IDENTIFIER, literal=value)
    
    def handle_comment(self):
        while self.peek() != '\n' and not self.is_at_end():
            self.advance()
    
    def add_token(self, type, lexeme='', literal=None):
        lexeme = lexeme if lexeme != '' else self.source[self.start:self.current]
        self.tokens.append(Token(type, lexeme, literal, self.line))
    
    def advance(self):
        self.current += 1
        return self.source[self.current - 1]
    
    def peek(self):
        if self.current >= len(self.source): return '\0'
        return self.source[self.current]
    
    def peek2(self):
        if self.current + 1 >= len(self.source): return '\0'
        return self.source[self.current + 1]
    
    def is_at_end(self):
        return self.current >= len(self.source)