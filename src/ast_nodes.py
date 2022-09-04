from typing import Any
from dataclasses import dataclass

from src.tokens import Token
from src.visitor import Visitee

class AstNode(Visitee): pass

### Expressions
@dataclass
class Literal(AstNode):
    value: Any
@dataclass
class Unary(AstNode):
    operator: Token
    expression: AstNode
@dataclass
class Binary(AstNode):
    left: AstNode
    operator: Token
    right: AstNode
@dataclass
class Grouping(AstNode):
    expression: AstNode
@dataclass
class Variable(AstNode):
    name: Token
@dataclass  
class Range(AstNode):
    low: AstNode
    high: AstNode
    step: AstNode
@dataclass
class FunctionCall(AstNode):
    callee: AstNode
    arguments: list[AstNode]

### Statements
@dataclass
class Block(AstNode):
    statements: list[AstNode]
@dataclass
class ExpressionStatement(AstNode):
    expression: AstNode
@dataclass
class PrintStatement(AstNode):
    expression: AstNode
@dataclass
class AssignmentStatement(AstNode):
    name: Token
    operator: Token
    value: AstNode
@dataclass
class EachStatement(AstNode):
    var_name: Token
    iterable: AstNode
    body: Block
@dataclass
class IfStatement(AstNode):
    condition: AstNode
    main_branch: Block
    else_branch: AstNode
@dataclass
class WhileStatement(AstNode):
    condition: AstNode
    body: Block
@dataclass  
class FunctionDefinition(AstNode):
    parameters: list[Token]
    body: Block
@dataclass
class ReturnStatement(AstNode):
    value: AstNode
@dataclass
class BreakStatement(AstNode):
    pass