from src.ast_nodes import FunctionDefinition

class Return(Exception):
    def __init__(self, value):
        super().__init__()
        self.value = value

class NathCallable(): pass

class NathFunction(NathCallable):
    def __init__(self, interpreter, definition: FunctionDefinition):
        self.interpreter = interpreter
        self.definition = definition
        self.arity = len(definition.parameters)

    def call(self, *arguments):
        self.interpreter.env.new_scope()
        for param, arg in zip(self.definition.parameters, arguments):
            self.interpreter.env.local_scope.assign(param, arg)

        try: 
            self.interpreter.evaluate(self.definition.body)
        except Return as r:
            return r.value
            
        self.interpreter.env.destroy_scope()
        return None