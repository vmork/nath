from copy import deepcopy

from src.errors import NathRuntimeError
from src.tokens import Token

MISSING = object()

class Environment():
    def __init__(self, parent=None):
        self.dict = {}
        self.parent = parent
        
    def assign_or_define(self, name: str, value):
        did_assign = self.assign(name, value)
        if not did_assign:
            self.define(name, value)
 
    def assign(self, name, value):
        if self.dict.get(name) is not None:
            self.dict[name] = value 
            return True
        elif self.parent is not None: 
            self.parent.assign(name, value)
        else: 
            return False
    
    def define(self, name, value):
        self.dict[name] = value

    def get_or_MISSING(self, token: Token):
        value = self.dict.get(token.lexeme, MISSING)
        if value is MISSING and self.parent is not None: 
            return self.parent.get_or_MISSING(token)
        return value

    def get_or_error(self, token: Token):
        value = self.get_or_MISSING(token)
        if value is MISSING:
            raise NathRuntimeError(token, f"Undefined variable '{token.lexeme}'")
        return value