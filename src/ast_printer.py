from src.tokens import Token
from src.visitor import Visitor
import src.ast_nodes as ast

class AstPrinter(Visitor):
    '''Prints the abstract syntax tree of an expression. 
       ie ``Binary(Literal(1), Token('+'), Literal(1)`` -> ``+(1,1)``'''
    
    def __init__(self):
        self.indent_level = 0

    def print(self, expr):
        return self.visit(expr)
    
    def default(self, expr):
        return f"{type(expr).__name__}{self.recurse(list(expr.__dict__.values()))}"

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
        return f"print{self.recurse([stmt.expression])}"
    def visit_AssignmentStatement(self, stmt):
        return f"{stmt.operator.lexeme}({stmt.name.lexeme},{self.recurse([stmt.value], paren=False)})"
    def visit_Variable(self, expr):
        return f"var({expr.name.lexeme})"
    def visit_Block(self, block):
        self.indent_level += 1
        return "block(\n"+ "    " * self.indent_level + \
            self.recurse(block.statements, sep="\n"+"    " * self.indent_level) + ")"
    def visit_Range(self, range):
        return f"range{self.recurse([range.low, range.high, range.step])}"
    def visit_EachStatement(self, expr: ast.EachStatement):
        return f"each({expr.var_name.lexeme if expr.var_name else 'null'}, {self.recurse([expr.body], paren=False)})"
    def visit_WhileStatement(self, expr: ast.WhileStatement):
        return f"while{self.recurse([expr.body])}"
    
    def recurse(self, exprs: list, paren=True, sep=','):
        vals = []
        for expr in exprs:
            if expr is None: vals.append('null')
            elif isinstance(expr, list): vals.append(f"[{self.recurse(expr, paren=False)}]")
            elif isinstance(expr, Token): vals.append(expr.lexeme)
            else: vals.append(expr.accept(self))
        s = sep.join(str(v) for v in vals)
        return f"({s})" if paren else s