from src.visitor import Visitor

class AstPrinter(Visitor):
    '''Prints the abstract syntax tree of an expression. 
       ie ``Binary(Literal(1), Token('+'), Literal(1)`` -> ``+(1,1)``'''

    def print(self, expr):
        return self.visit(expr)
    
    def default(self, expr):
        return f"{type(expr).__name__}({self.recurse(list(expr.__dict__.values()))})"

    def visit_Literal(self, expr):
        return expr.value if expr.value is not None else "null"
    def visit_Unary(self, expr):
        return f"{expr.operator.lexeme}{self.recurse([expr.expression])}"
    def visit_Binary(self, expr):
        return f"{expr.operator.lexeme}{self.recurse([expr.left, expr.right])}"
    def visit_Grouping(self, expr):
        return f"group{self.recurse([expr.expression])}"
    def visit_ExpressionStatement(self, stmt):
        return f"stmt{self.recurse([stmt.expression])}"
    def visit_PrintStatement(self, stmt):
        return f"print({self.recurse([stmt.expression])})"
    def visit_AssignmentStatement(self, stmt):
        return f"{stmt.operator.lexeme}({stmt.name.lexeme},{self.recurse([stmt.value], paren=False)})"
    def visit_Variable(self, expr):
        return f"var({expr.name.lexeme})"
    def visit_Block(self, block):
        return "block" + self.recurse(block.statements, sep='\n    ')
    def visit_Range(self, range):
        return f"range{self.recurse([range.low, range.high, range.step])}"
    
    def recurse(self, exprs: list, paren=True, sep=','):
        s = sep.join([str(expr.accept(self)) if expr else 'null' for expr in exprs])
        return f"({s})" if paren else s