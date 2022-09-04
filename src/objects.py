from src.ast_nodes import FunctionDefinition
from src.environment import Environment

class Return(Exception):
    def __init__(self, value):
        super().__init__()
        self.value = value

class Break(Exception): pass

class NathFunction():
    def __init__(self, interpreter=None, definition: FunctionDefinition=None, closure: Environment=None, name=None):
        self.interpreter = interpreter
        self.definition = definition
        self.closure = closure
        if definition: self.arity = len(definition.parameters)
        self.name = name

    def call(self, *arguments):
        #print("in call,", arguments)
        env = Environment(parent=self.closure)
        for param, arg in zip(self.definition.parameters, arguments):
            env.define(param.lexeme, arg)

        #print("environment:", env.dict, "parent:", env.parent.dict)

        try: 
            self.interpreter.evaluate(self.definition.body, block_env=env)
        except Return as r:
            return r.value
    
    def __repr__(self):
        if self.name: return f"function '{self.name}'"
        else: return "anonymous function"
