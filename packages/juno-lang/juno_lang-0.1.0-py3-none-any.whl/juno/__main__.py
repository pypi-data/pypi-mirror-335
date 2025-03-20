"""
Main entry point for the Juno programming language interpreter.
"""

import argparse
import sys
import juno
from juno.interpreter.interpreter import Interpreter

def main():
    """Main entry point for the Juno interpreter."""
    parser = argparse.ArgumentParser(description="Juno Programming Language Interpreter")
    parser.add_argument('--version', action='store_true', help='Show version information')
    parser.add_argument('--repl', action='store_true', help='Start interactive REPL mode')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--optimize', action='store_true', default=True, help='Enable JIT optimization')
    parser.add_argument('filename', nargs='?', help='Path to the Juno source file')
    
    args = parser.parse_args()
    
    if args.version:
        print(f"Juno version {juno.__version__}")
        return
    
    try:
        interpreter = Interpreter(debug=args.debug, optimize=args.optimize)
        
        if args.repl:
            run_repl(interpreter)
        elif args.filename:
            run_file(interpreter, args.filename)
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def run_file(interpreter, filename):
    """Execute a Juno source file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        interpreter.execute(source, filename)
    except FileNotFoundError:
        print(f"Error: Could not find file '{filename}'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error executing '{filename}': {e}", file=sys.stderr)
        sys.exit(1)

def run_repl(interpreter):
    """Start an interactive Read-Eval-Print Loop (REPL)."""
    print(f"Juno REPL v{juno.__version__}")
    print("Type 'exit' or 'quit' to exit")
    
    multiline_input = []
    multiline_mode = False
    
    while True:
        try:
            prompt = "... " if multiline_mode else ">>> "
            line = input(prompt)
            
            if line in ('exit', 'quit'):
                break
            
            # Handle multiline input
            if line.endswith('{'):
                multiline_mode = True
                multiline_input.append(line)
                continue
            elif multiline_mode:
                multiline_input.append(line)
                if line == '}':
                    multiline_mode = False
                    source = '\n'.join(multiline_input)
                    result = interpreter.execute(source, "<repl>")
                    if result is not None:
                        print(f"=> {result}")
                    multiline_input = []
                continue
            
            # Execute single line input
            result = interpreter.execute(line, "<repl>")
            if result is not None:
                print(f"=> {result}")
                
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")
            multiline_input = []
            multiline_mode = False
        except EOFError:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            multiline_input = []
            multiline_mode = False

if __name__ == "__main__":
    main()