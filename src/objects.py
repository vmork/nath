from src.ast_nodes import FunctionDefinition
from src.environment import Environment

class Return(Exception):
    def __init__(self, value):
        super().__init__()
        self.value = value

class NathCallable(): pass

class NathFunction(NathCallable):
    def __init__(self, interpreter, definition: FunctionDefinition, closure: Environment):
        self.interpreter = interpreter
        self.definition = definition
        self.closure = closure
        self.arity = len(definition.parameters)

    def call(self, *arguments):
        #print("in call,", arguments)
        env = Environment(parent=self.closure)
        for param, arg in zip(self.definition.parameters, arguments):
            env.define(param.lexeme, arg)
            
        #print("environment:", env.dict, "parent:", env.parent.dict)

        try: 
            self.interpreter.execute_block(self.definition.body, env)
        except Return as r:
            return r.value

    def __repr__(self):
        return f"<function>"