#!/usr/bin/env python3
"""
Juno Debugger

This tool provides debugging capabilities for Juno programs.
"""

import argparse
import os
import sys
import cmd
import readline
import traceback

from juno.interpreter import Interpreter
from juno.lexer import Lexer
from juno.parser import Parser

class JunoDebugger(cmd.Cmd):
    """Interactive debugger for Juno programs."""
    
    intro = "Juno Debugger. Type 'help' for help."
    prompt = "(jdb) "
    
    def __init__(self, file_path):
        """
        Initialize the debugger.
        
        Args:
            file_path (str): Path to the Juno file to debug
        """
        super().__init__()
        self.file_path = file_path
        self.interpreter = Interpreter(debug=True, optimize=False)
        self.breakpoints = []
        self.current_line = 0
        self.source_lines = []
        self.running = False
        self.step_mode = False
        
        # Load the source file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.source = f.read()
                self.source_lines = self.source.split('\n')
        except Exception as e:
            print(f"Error loading file: {e}", file=sys.stderr)
            sys.exit(1)
    
    def do_run(self, arg):
        """Run the program from the beginning."""
        self.running = True
        self.current_line = 0
        
        try:
            # Parse the program
            lexer = Lexer(self.source, self.file_path)
            tokens = lexer.scan_tokens()
            parser = Parser(tokens, self.file_path)
            ast = parser.parse()
            
            # Execute the program with debugging
            self._debug_execute(ast)
        
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
    
    def do_break(self, arg):
        """Set a breakpoint at the specified line number."""
        try:
            line = int(arg.strip())
            if line < 1 or line > len(self.source_lines):
                print(f"Invalid line number: {line}")
                return
            
            if line in self.breakpoints:
                print(f"Breakpoint already set at line {line}")
            else:
                self.breakpoints.append(line)
                print(f"Breakpoint set at line {line}")
        except ValueError:
            print("Please specify a valid line number")
    
    def do_clear(self, arg):
        """Clear a breakpoint at the specified line number."""
        if not arg:
            self.breakpoints = []
            print("All breakpoints cleared")
            return
        
        try:
            line = int(arg.strip())
            if line in self.breakpoints:
                self.breakpoints.remove(line)
                print(f"Breakpoint cleared at line {line}")
            else:
                print(f"No breakpoint at line {line}")
        except ValueError:
            print("Please specify a valid line number")
    
    def do_list(self, arg):
        """List source code around the current line."""
        if not self.source_lines:
            print("No source code loaded")
            return
        
        start = max(0, self.current_line - 5)
        end = min(len(self.source_lines), self.current_line + 5)
        
        for i in range(start, end):
            prefix = "-> " if i == self.current_line - 1 else "   "
            prefix += "B " if i + 1 in self.breakpoints else "  "
            print(f"{prefix}{i + 1}: {self.source_lines[i]}")
    
    def do_step(self, arg):
        """Step to the next line of code."""
        self.step_mode = True
        if not self.running:
            self.do_run("")
        else:
            return True
    
    def do_continue(self, arg):
        """Continue execution until the next breakpoint."""
        self.step_mode = False
        if not self.running:
            self.do_run("")
        else:
            return True
    
    def do_print(self, arg):
        """Print the value of a variable."""
        if not arg:
            print("Please specify a variable name")
            return
        
        try:
            # Evaluate the expression
            result = self.interpreter.execute(arg, "<debugger>")
            print(f"{arg} = {result}")
        except Exception as e:
            print(f"Error: {e}")
    
    def do_quit(self, arg):
        """Quit the debugger."""
        print("Exiting debugger")
        return True
    
    def do_help(self, arg):
        """Show help message."""
        if not arg:
            print("Available commands:")
            print("  run       - Run the program from the beginning")
            print("  break N   - Set a breakpoint at line N")
            print("  clear [N] - Clear breakpoint at line N or all breakpoints")
            print("  list      - List source code around the current line")
            print("  step      - Step to the next line of code")
            print("  continue  - Continue execution until the next breakpoint")
            print("  print X   - Print the value of variable X")
            print("  quit      - Quit the debugger")
            print("  help      - Show this help message")
        else:
            cmd.Cmd.do_help(self, arg)
    
    def _debug_execute(self, ast):
        """
        Execute the AST with debugging.
        
        Args:
            ast: The abstract syntax tree to execute
        """
        # This is a simplified implementation
        # A real debugger would need to instrument the AST or interpreter
        
        print("Starting program execution...")
        print("Use 'step' to step through the program or 'continue' to run to the next breakpoint.")
        
        # For now, just execute the program
        try:
            result = self.interpreter.execute(self.source, self.file_path)
            print("\nProgram execution completed.")
            if result is not None:
                print(f"Result: {result}")
        except Exception as e:
            print(f"\nProgram execution failed: {e}")
            traceback.print_exc()

def main():
    """Main entry point for the debugger."""
    parser = argparse.ArgumentParser(description="Juno Debugger")
    parser.add_argument('file', help='Juno file to debug')
    
    args = parser.parse_args()
    
    if not os.path.isfile(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    if not args.file.endswith('.juno'):
        print(f"Warning: File does not have .juno extension: {args.file}")
    
    debugger = JunoDebugger(args.file)
    debugger.cmdloop()

if __name__ == "__main__":
    main()