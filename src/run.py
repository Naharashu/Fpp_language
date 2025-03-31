import sys
import fpp
import os

def run_file(filename):
    full_path = os.path.abspath(filename)
    
    if not filename.endswith('.fpp'):
        print(f"Error: File '{filename}' should have .fpp extension.")
        return

    print(f"Attempting to open file: {full_path}")
    
    if not os.path.exists(full_path):
        print(f"Error: File '{full_path}' not found.")
        print(f"Current working directory: {os.getcwd()}")
        return

    try:
        with open(full_path, 'r', encoding='utf-8') as file:
            script = file.read()
    except IOError as e:
        print(f"Error: Could not read file '{full_path}'. Details: {str(e)}")
        return


    lexer = fpp.Lexer(filename, script)
    tokens, error = lexer.make_tokens()
    if error:
        print(error.as_string())
        return


    parser = fpp.Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return


    interpreter = fpp.Interpreter()
    context = fpp.Context('<program>')
    context.symbol_table = fpp.SymbolTable()
    result = interpreter.visit(ast.node, context)

    if result.error:
        print(result.error.as_string())
    elif result.value:
        if isinstance(result.value, fpp.Value):  
            print(result.value)
        elif hasattr(result.value, 'elements'):
            if len(result.value.elements) == 1:
                print(repr(result.value.elements[0]))
            else:
                print(repr(result.value))
        else:
            print(repr(result.value))
            
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run.py <filename>")
    else:
        run_file(sys.argv[1])