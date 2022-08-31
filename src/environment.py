from src.errors import NathRuntimeError
from src.tokens import Token

MISSING = object()

class Scope():
    def __init__(self, parent=None):
        self.parent: Scope = parent
        self.dict = {}

    def assign(self, token: Token, value):
        if type(value) == int: value = float(value)
        self.dict[token.lexeme] = value 

    def assign_name(self, name: str, value):
        if type(value) == int: value = float(value)
        self.dict[name] = value

class Environment():
    def __init__(self):
        self.global_scope = Scope()
        self.local_scope = self.global_scope
    
    def new_scope(self):
        scope = Scope(parent=self.local_scope)
        scope.dict = scope.parent.dict.copy()
        self.local_scope = scope
    
    def destroy_scope(self):
        self.local_scope = self.local_scope.parent

    def get_or_MISSING(self, token: Token):
        return self.local_scope.dict.get(token.lexeme, MISSING)

    def get_or_error(self, token: Token):
        value = self.get_or_MISSING(token)
        if value is MISSING:
            raise NathRuntimeError(token, f"Undefined variable '{token.lexeme}'")
        return value