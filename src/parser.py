from src.errors import NathSyntaxError
import src.ast_nodes as ast
from src.tokens import Token, TokenType as tt

class Parser():
    def __init__(self):
        self.ignore_undefined = False
    
    def parse(self, tokens: list[Token]) -> list:
        '''Recursively parse self.tokens and return a list of statements.'''
        self.tokens = tokens
        self.current = 0
        statements = []
        self.line_num = 0
        self.inside_function_body = False
        self.inside_each_or_while = False
        while not self.is_at_end():
            self.line_num += 1
            statements.append((self.statement(), self.line_num))
            self.match([tt.EOF])
        return statements
    
    ### Helper methods
    def is_at_end(self):
        return self.current >= len(self.tokens)
    
    def advance(self):
        if not self.is_at_end(): self.current += 1
        return self.previous()
    
    def previous(self):
        return self.tokens[self.current - 1]
    
    def peek(self):
        if self.is_at_end(): return Token(tt.EOF)
        return self.tokens[self.current]
    
    def match(self, token_types: list[str], consume=True):
        next_token = self.peek()
        if any([next_token.istype(t) for t in token_types]):
            return self.advance() if consume else True
        return None

    def has_to_match(self, token_types: list[str], error_msg: str, consume=True):
        token = self.match(token_types, consume)
        if not token:
            raise NathSyntaxError(self.peek(), error_msg) # stop parsing
        else: return token
    
    def is_number(self, expr: ast.AstNode):
        if isinstance(expr, ast.Literal) and isinstance(expr.value, float): 
            return True 
        return False
    
    def consume_newlines(self):
        while self.match([tt.NEWLINE]): pass # ignore empty lines
    
    ### Recursive descent methods
    def statement(self):
        self.consume_newlines()

        if self.match([tt.PRINT]):
            stmt = self.print_statement()
        elif self.match([tt.LEFT_BRACE]):
            stmt = self.block()
        elif self.match([tt.EACH]):
            stmt = self.each_statement()
        elif self.match([tt.WHILE]):
            stmt = self.while_statement()
        elif self.match([tt.IF]):
            stmt = self.if_statement()
        elif self.match([tt.RETURN]):
            stmt = self.return_statement()
        elif self.match([tt.BREAK]):
            stmt = self.break_statement()
        elif self.match([tt.CONTINUE]):
            stmt = self.continue_statement()
        else:
            stmt = self.assignment_or_expression_statement()
        
        if not self.peek().type in [tt.RIGHT_BRACE]:
            self.has_to_match([tt.NEWLINE, tt.EOF, tt.SEMICOLON], 
                f"Excpected end of statement (newline or ';'), but got {self.peek().lexeme}")

        self.consume_newlines()
        return stmt
    
    def block(self):
        statements = []
        while not (self.is_at_end() or self.peek().istype(tt.RIGHT_BRACE)):
            statements.append(self.statement())
        self.has_to_match([tt.RIGHT_BRACE], "Brace mismatch")
        return ast.Block(statements)
    
    def each_statement(self):
        var_name = self.expression()
        if self.match([tt.OF]):
            iterable = self.expression()
            if not isinstance(var_name, ast.Variable):
                raise NathSyntaxError(var_name, f"Invalid variable name in each-statement")
            var_name = var_name.name
        else: var_name, iterable = None, var_name
        
        self.has_to_match([tt.LEFT_BRACE], "Excpected '{ after each-statement")
        self.inside_each_or_while = True
        body = self.block()
        self.inside_each_or_while = False
        return ast.EachStatement(var_name, iterable, body)
    
    def if_statement(self):
        condition = self.expression()
        self.has_to_match([tt.LEFT_BRACE], "Excpected '{' after if-statement")
        main_branch = self.block()

        # skip ahead to try to find 'else' or 'elseif'
        before_newlines_ref = self.current
        self.consume_newlines() 

        if self.match([tt.ELSEIF]):
            else_branch = self.if_statement()
        elif self.match([tt.ELSE]):
            self.has_to_match([tt.LEFT_BRACE], "Excpected '{' after elseif-statement")
            else_branch = self.block()
        else: 
            self.current = before_newlines_ref # if we skipped newlines earlier, go back
            else_branch = None
        return ast.IfStatement(condition, main_branch, else_branch)
    
    def while_statement(self):
        condition = self.expression()
        self.has_to_match([tt.LEFT_BRACE], "Excpected '{' after while-statement")
        self.inside_each_or_while = True
        body = self.block()
        self.inside_each_or_while = False
        return ast.WhileStatement(condition, body)
            
    def print_statement(self):        
        return ast.PrintStatement(self.expression())
    
    def assignment_or_expression_statement(self):
        expr = self.expression()
        operator = self.match([tt.EQUAL, tt.STAR_EQUAL, tt.SLASH_EQUAL, tt.MINUS_EQUAL, tt.PLUS_EQUAL, tt.CARET_EQUAL])
        if operator is not None: return self.assignment_statement(expr, operator)
        return ast.ExpressionStatement(expr)
    
    def assignment_statement(self, expr, operator):
        if not isinstance(expr, ast.Variable): 
            raise NathSyntaxError(operator, f"Assignment target is not a valid variable name")
        value = self.expression()
        return ast.AssignmentStatement(expr.name, operator, value)
    
    def return_statement(self):
        if not self.inside_function_body:
            raise NathSyntaxError(self.peek(), "Return statement outside of function body")
        if self.match([tt.NEWLINE, tt.SEMICOLON, tt.EOF], consume=False): value = None
        else: value = self.expression()
        return ast.ReturnStatement(value)
    
    def break_statement(self):
        if not self.inside_each_or_while:
            raise NathSyntaxError(self.peek(), "Break statement outside each or while loop")
        return ast.BreakStatement()
    
    def expression(self):
        return self.function_definition()
    
    def function_definition(self): # TODO: separate into param_list(), tt.ARROW, fn_body()
        param_list = []
        left_paren = self.match([tt.LEFT_PAREN])
        if var := self.match([tt.IDENTIFIER]):
            param_list.append(var)
            while self.match([tt.COMMA]):
                if var := self.match([tt.IDENTIFIER]): param_list.append(var)
                else: raise NathSyntaxError(self.peek(), "Trailing comma in parameter list")

            if left_paren: 
                right_paren = self.match([tt.RIGHT_PAREN])
                
            if self.match([tt.ARROW]):
                self.inside_function_body = True
                expr = self.finish_function_definition(param_list)
                self.inside_function_body = False
                if left_paren and right_paren is None: 
                    expr = ast.Grouping(expr)
                    self.match([tt.RIGHT_PAREN])
                return expr
            elif len(param_list) == 1:
                if left_paren: 
                    if right_paren: self.current -= 3
                    else: self.current -= 2
                else: self.current -= 1
                return self.range_expression()
            else:
                raise NathSyntaxError(var, "Expected '->' after argument list")

        elif left_paren:
            if self.match([tt.RIGHT_PAREN]) and self.match([tt.ARROW]):
                return self.finish_function_definition(param_list)
            else: self.current -= 1

        return self.range_expression()

    def finish_function_definition(self, param_list):
        if self.match([tt.LEFT_BRACE]): body = self.block()
        else: body = ast.Block([ast.ReturnStatement(self.expression())]) # implicit return stmt
        return ast.FunctionDefinition(param_list, body)

    def range_expression(self):
        low = self.logical_not()
        if self.match([tt.DOT_DOT]):
            high = self.logical_not()
            step = ast.Literal(1.0)
            if self.match([tt.DOT_DOT]):
                step = self.logical_not()
            return ast.Range(low, high, step)
        return low
    
    def logical_not(self): # same code as unary_left, but 'not' has lower precedence
        if operator := self.match([tt.NOT]):
            expr = self.logical_not()
            return ast.Unary(operator, expr)
        else: 
            return self.logical_binary()

    def binary_constructor(self, operators, next_fn):
        def f():
            expr: ast.AstNode = next_fn()
            while operator := self.match(operators):
                right: ast.AstNode = next_fn()
                expr = ast.Binary(expr, operator, right)
            return expr 
        return f
    
    def logical_binary(self):
        return self.binary_constructor([tt.AND, tt.OR], 
            self.equality)()

    def equality(self):
        return self.binary_constructor([tt.EQUAL_EQUAL, tt.BANG_EQUAL], 
            self.comparison)()
    
    def comparison(self):
        return self.binary_constructor([tt.GT, tt.GT_EQUAL, tt.LT, tt.LT_EQUAL], 
            self.term)()
    
    def term(self):
        return self.binary_constructor([tt.PLUS, tt.MINUS], 
            self.factor)()
    
    def factor(self):
        return self.binary_constructor([tt.STAR, tt.SLASH], 
            self.unary_left)()

    def unary_left(self):
        if operator := self.match([tt.MINUS, tt.PLUS]):
            expr = self.unary_left()
            return ast.Unary(operator, expr)
        return self.implicit_multiplication()

    def implicit_multiplication(self):
        lhs = self.power()
        next_tok = self.peek()
        if self.is_number(lhs) and next_tok.type in [tt.IDENTIFIER, tt.LEFT_PAREN]:
            rhs = self.implicit_multiplication()
            mul_op = Token(tt.STAR, '*', None, next_tok.line_num)
            return ast.Binary(lhs, mul_op, rhs)
        return lhs
    
    def power(self):
        return self.binary_constructor([tt.CARET], 
            self.unary_right)()
        
    def unary_right(self, expr=None):
        if expr is None: 
            expr = self.function_call()
        if operator := self.match([tt.BANG]):
            expr = self.unary_right(expr)
            return ast.Unary(operator, expr)
        return expr
    
    def function_call(self):
        expr = self.primary()
        while self.match([tt.LEFT_PAREN]):
            expr = self.finish_call(expr)
        return expr
    def finish_call(self, calle):
        arguments = []
        if not self.match([tt.RIGHT_PAREN], consume=False):
            arguments.append(self.range_expression())
            while self.match([tt.COMMA]):
                arguments.append(self.range_expression())
        self.has_to_match([tt.RIGHT_PAREN], "Parenthesis mismatch")
        return ast.FunctionCall(calle, arguments)
    
    def primary(self):
        if self.match([tt.TRUE]): return ast.Literal(True)
        if self.match([tt.FALSE]): return ast.Literal(False)
        if self.match([tt.NULL]): return ast.Literal(None)
        if name := self.match([tt.IDENTIFIER]): 
            return ast.Variable(name)
        if token := self.match([tt.STRING, tt.NUMBER]):
            return ast.Literal(token.literal)
        if self.match([tt.LEFT_PAREN]):
            expr = self.expression()
            self.has_to_match([tt.RIGHT_PAREN], "Parenthesis mismatch")
            return ast.Grouping(expr)
        raise NathSyntaxError(self.peek(), "Expected expression")