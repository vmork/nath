import sys

from src import scanner, parser, ast_printer, interpreter, repl
from src.errors import report_error, NathRuntimeError, NathSyntaxError

class NathRuntime():
    def __init__(self, in_repl=False):
        self.parser = parser.Parser() 
        self.interpreter = interpreter.Interpreter(in_repl=in_repl)

    def run_file(self, filename):
        with open(filename) as f:
            text = f.read()
            print('source text:', repr(text))
            opcode = self.run(text)
            if opcode != 0:
                sys.exit(opcode)

    def run(self, source):
        try: ### scan
            _scanner = scanner.Scanner(source)
            tokens =  _scanner.scan_tokens()
            print('tokens:', [t.type for t in tokens])
        except NathSyntaxError as e:
            report_error(e)
            return 65
        try: ### parse
            statements = self.parser.parse(tokens)
            printer = ast_printer.AstPrinter()
            print("ast:")
            try:
                for i, (stmt, _) in enumerate(statements):
                    print(f"{i}: {printer.print(stmt)}")
            except Exception as e:
                print("Can't print ast,", e)
            
        except NathSyntaxError as e:
            report_error(e)
            return 65
        try: ### interpret
            print('bindings:', self.interpreter.env.dict, '\n')
            self.interpreter.interpret(statements)
        except NathRuntimeError as e:
            report_error(e)
            return 70
        return 0

def main():
    if len(sys.argv) > 2:
        print("Usage: python nath.py [path]")
        sys.exit(1)
    elif len(sys.argv) == 2:
        runtime = NathRuntime()
        runtime.run_file(sys.argv[1])
    else: 
        repl.run()

if __name__ == '__main__':
    main()