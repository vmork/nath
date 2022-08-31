from termcolor import colored
from src.tokens import Token

class NathError(Exception): 
    def __init__(self, where: Token|int, msg: str):
        super().__init__(msg)
        self.msg = msg
        self.where = where

class NathRuntimeError(NathError): pass
class NathSyntaxError(NathError): pass

err_names = {
    'NathRuntimeError': 'Runtime error',
    'NathSyntaxError': 'Syntax error',
}

def report_error(err): 
    err_name = err_names[type(err).__name__]
    # err.where is either a Token or an int representing the line number where the error occurred
    if isinstance(err.where, Token):
        where_str = ' at ' + err.where.lexeme if err.where.type != 'EOF' else ' at end'
        line_num = err.where.line_num
    elif isinstance(err.where, int):
        line_num, where_str = err.where, ''
    else: raise ValueError(f'Invalid error location: {err.where}')

    first = f"{err_name}! [line {line_num}{where_str}]:"
    print(
        colored(first, 'red', attrs=['underline']) + ' ' + \
        err.msg
    )
