from typing import Any, Tuple
import math

from src.environment import Environment, MISSING
import src.ast_nodes as ast
from src.tokens import Token, TokenType as tt
from src.errors import NathRuntimeError
from src.visitor import Visitor, Visitee
from src.objects import NathCallable, NathFunction, Return, Break
from src import nath_builtins

class Interpreter(Visitor):
    def __init__(self, in_repl=False):
        self.in_repl = in_repl
        self.global_scope = Environment()
        self.env = self.global_scope

        # add builtin functions to global scope
        for name, arity in nath_builtins.functions: 
            func = NathCallable()
            func.arity = arity
            func.call = getattr(nath_builtins, f"_{name}")
            self.global_scope.define(name, func)

    ### API entry point
    def interpret(self, statements: list[Tuple[int, ast.AstNode]]) -> None:
        for stmt, i in statements:
            self.stmt_line_num = i # for printing errors when we dont know the exact token we're at
            self.evaluate(stmt)
    
    ### Helper methods ----------------------------------------------------------------
    def evaluate(self, expr_or_stmt, *args, **kwargs):
        return self.visit(expr_or_stmt, *args, **kwargs)

    def stringify(self, val):
        if val is None: return "null"
        if val is True: return "true"
        if val is False: return "false"
        if isinstance(val, float):
            text = str(val)
            if text.endswith(".0"): return text[:-2]
            return text
        return val

    def assert_types(self, token, vals: list, types: tuple, same_types=True, msg: str=None):
        types = tuple(types)
        for v in vals:
            if not isinstance(v, types):
                msg = msg or f"Operands to {token.lexeme} must be of type " + \
                             f"[{' or '.join([t.__name__ for t in types])}], " + \
                             f"but have types {[type(v).__name__ for v in vals]}"
                raise NathRuntimeError(token, msg)
    
    def assert_int_like(self, value):
        if int(value) == value:
            return int(value)
        return None

    def is_truthy(self, val: Any) -> bool:
        # just use the same rules as python for now (empty iterables, 0 and None are falsy)
        return bool(val)

    def is_equal(self, a: Any, b: Any) -> bool:
        return a == b # same as python
    
    def logical_binary(self, expr: ast.Binary):
        left = self.evaluate(expr.left)
        if expr.operator.type == tt.OR:
            if self.is_truthy(left): return left
        else: 
            if not self.is_truthy(left): return left
        return self.evaluate(expr.right)


    ### Visitor methods ---------------------------------------------------------------
    def visit_Block(self, block: ast.Block, block_env=None) -> None:
        if block_env is None: block_env = self.env

        prev_env = self.env
        try:
            self.env = block_env
            for stmt in block.statements: 
                self.evaluate(stmt)
        finally:
            self.env = prev_env

    def visit_EachStatement(self, stmt: ast.EachStatement) -> None:
        iterable = self.evaluate(stmt.iterable)
        if not isinstance(iterable, (list, str)):
            raise NathRuntimeError(-69, f"Can't loop over object of type '{type(iterable).__name__}'")

        loop_varname_scope = Environment(parent=self.env.parent)
        self.env.parent = loop_varname_scope
        try:
            for elem in iterable:
                if stmt.var_name:
                    loop_varname_scope.define(stmt.var_name.lexeme, elem)
                self.evaluate(stmt.body)
        except Break: pass
        finally:
            self.env.parent = self.env.parent.parent
    
    def visit_WhileStatement(self, stmt: ast.WhileStatement):
        try:
            while self.is_truthy(self.evaluate(stmt.condition)):
                self.evaluate(stmt.body)
        except Break: pass
    
    def visit_IfStatement(self, stmt: ast.IfStatement) -> None:
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.evaluate(stmt.main_branch)
        elif stmt.else_branch is not None:
            self.evaluate(stmt.else_branch)
            
    def visit_PrintStatement(self, stmt: ast.PrintStatement) -> None:
        print(self.evaluate(stmt.expression))
    
    def visit_ExpressionStatement(self, stmt: ast.ExpressionStatement) -> None:
        result = self.evaluate(stmt.expression)
        if self.in_repl: print(self.stringify(result))
    
    def visit_AssignmentStatement(self, stmt: ast.AssignmentStatement) -> None:
        var = stmt.name
        lhs = self.env.get_or_MISSING(var)
        if lhs is MISSING and stmt.operator.type != tt.EQUAL:
            raise NathRuntimeError(stmt.operator, 
            f"'{stmt.operator.lexeme}' on undefined variable {var.lexeme}")

        rhs = self.evaluate(stmt.value)
        match(stmt.operator.type):
            case tt.EQUAL: value = rhs
            case tt.PLUS_EQUAL: value = lhs + rhs
            case tt.MINUS_EQUAL: value = lhs - rhs
            case tt.STAR_EQUAL: value = lhs * rhs
            case tt.SLASH_EQUAL: value = lhs / rhs
            case tt.CARET_EQUAL: value = lhs ** rhs
        
        self.env.assign_or_define(var.lexeme, value)
    
    def visit_FunctionDefinition(self, expr: ast.FunctionDefinition):
        return NathFunction(interpreter=self, definition=expr, closure=self.env)
    
    def visit_FunctionCall(self, expr: ast.FunctionCall):
        callee = self.evaluate(expr.callee)
        if not isinstance(callee, NathCallable):
            raise NathRuntimeError(-69, f"{type(callee).__name__} is not callable")

        arguments = [self.evaluate(arg) for arg in expr.arguments]
        if len(arguments) != callee.arity:
            raise NathRuntimeError(-69, f"Expected {callee.arity} arguments but got {len(arguments)}")
        return callee.call(*arguments)
    
    def visit_ReturnStatement(self, stmt: ast.ReturnStatement):
        if stmt.value is not None: 
            value = self.evaluate(stmt.value)
        else: value = None
        raise Return(value)
    
    def visit_BreakStatement(self, stmt: ast.BreakStatement):
        raise Break()
    
    def visit_Range(self, r: ast.Range):
        args = [r.low, r.high, r.step]
        args = [self.assert_int_like(self.evaluate(x)) for x in args]
        if any([x is None for x in args]):
            raise NathRuntimeError(-69, "Arguments to range constructor low..high..step must be integers")
        return [float(x) for x in range(args[0], args[1]+1, args[2])]
            
    def visit_Variable(self, var: ast.Variable):
        return self.env.get_or_error(var.name)

    def visit_Literal(self, expr: ast.Literal):
        return expr.value

    def visit_Grouping(self, expr: ast.Grouping):
        return self.visit(expr.expression)

    def visit_Unary(self, expr: ast.Unary):
        expr_val = self.evaluate(expr.expression)
        match(expr.operator.type):
            case tt.MINUS: 
                self.assert_types(expr.operator, [expr_val], [float])
                return -expr_val
            case tt.PLUS: 
                self.assert_types(expr.operator, [expr_val], [float])
                return expr_val
            case tt.NOT: 
                return not self.is_truthy(expr_val)
            case tt.BANG:
                self.assert_types(expr.operator, [expr_val], [float])
                expr_val_int = int(expr_val)
                if not expr_val_int == expr_val:
                    raise NathRuntimeError(expr.operator, 
                    f"Factorial operator '!' doesnt take decimal numbers, but received {expr_val}")
                return float(math.factorial(expr_val_int))

    def visit_Binary(self, expr: ast.Binary):
        if expr.operator.type in [tt.AND, tt.OR]:
            return self.logical_binary(expr)
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        match(expr.operator.type):
            case tt.PLUS: 
                if type(left) != type(right): # cant add strings and numbers
                    raise NathRuntimeError(expr.operator, 
                    "Operands to + must be of the same type, " + 
                    f"but have types {[type(left).__name__, type(right).__name__]}")
                self.assert_types(expr.operator, [left, right], [float, str])
                return left + right
            case tt.MINUS: 
                self.assert_types(expr.operator, [left, right], [float])
                return left - right
            case tt.STAR: 
                self.assert_types(expr.operator, [left, right], [float])
                return left * right
            case tt.SLASH: 
                self.assert_types(expr.operator, [left, right], [float])
                if right == 0:
                    raise NathRuntimeError(expr.operator, "Division by zero")
                return left / right
            case tt.CARET:
                self.assert_types(expr.operator, [left, right], [float])
                return left ** right
            case tt.EQUAL_EQUAL: 
                return self.is_equal(left, right)
            case tt.BANG_EQUAL: 
                return not self.is_equal(left, right)
            case tt.GT: 
                self.assert_types(expr.operator, [left, right], [float])
                return left > right
            case tt.GT_EQUAL: 
                self.assert_types(expr.operator, [left, right], [float])
                return left >= right
            case tt.LT: 
                self.assert_types(expr.operator, [left, right], [float])
                return left < right
            case tt.LT_EQUAL: 
                self.assert_types(expr.operator, [left, right], [float])
                return left <= right
            case tt.AND:
                self.assert_types(expr.operator, [left, right], [bool])
                return left and right
            case tt.OR:
                self.assert_types(expr.operator, [left, right], [bool])
                return left or right