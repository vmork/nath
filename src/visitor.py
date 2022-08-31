### Visitors
class Visitor():
    def visit(self, visitee, *args, **kwargs):
        # the visitor figures out which method to call based on the class name of the 'visitee' instance
        # , this way we dont have to define accept methods for every visitee subclass
        visitee_name = type(visitee).__name__
        method =  getattr(self, f"visit_{visitee_name}", None) or getattr(self, "default", None)
        if method is None: 
            raise NotImplementedError(f"{type(self).__name__} has no method for class {visitee_name}")
        else: return method(visitee, *args, **kwargs)

class Visitee():
    '''Anything that can be visited by a Visitor() instance. 
       Only defines an accept() method that can be called like ``visitee.accept(visitor)``'''
    def accept(self, visitor, *args, **kwargs):
        return visitor.visit(self, *args, **kwargs)