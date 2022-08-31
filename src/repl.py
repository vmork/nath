from termcolor import colored
import main

def run():
    runtime = main.NathRuntime(in_repl=True)
    try: 
        while True:
            text = input(colored(">> ", 'green'))
            runtime.run(text)
    except EOFError: # exit repl on Ctrl-D
        print('Ctrl-D')