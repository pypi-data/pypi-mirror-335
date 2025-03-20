"""
Core interpreter for the Juno programming language.
"""

from juno.lexer import Lexer
from juno.parser import Parser
from juno.jit import JitCompiler
from juno.runtime import Runtime

class Interpreter:
    """
    Main class for the Juno language that coordinates lexing, parsing, and execution.
    """
    
    def __init__(self, debug=False, optimize=True):
        """
        Initialize the interpreter.
        
        Args:
            debug (bool): Enable debug mode for verbose output
            optimize (bool): Enable JIT optimization
        """
        self.debug = debug
        self.optimize = optimize
        self.runtime = Runtime()
        self.jit_compiler = JitCompiler(self.runtime)
    
    def execute(self, source, source_name):
        """
        Execute Juno source code.
        
        Args:
            source (str): The source code to execute
            source_name (str): The name of the source (file name or "<repl>")
            
        Returns:
            The result of the execution, if any
        """
        try:
            # Lexical analysis
            lexer = Lexer(source, source_name)
            tokens = lexer.scan_tokens()
            
            if self.debug:
                print("Tokens:", tokens)
            
            # Parsing
            parser = Parser(tokens, source_name)
            ast = parser.parse()
            
            if self.debug:
                print("AST:", ast)
            
            # Execution
            if self.optimize:
                # Use JIT compiler for optimization
                ast = self.jit_compiler.optimize(ast)
            
            # Interpret the code
            result = self.interpret(ast)
            
            return result
            
        except Exception as e:
            if self.debug:
                raise
            raise RuntimeError(f"{e}")
    
    def interpret(self, ast):
        """
        Interpret the abstract syntax tree.
        
        Args:
            ast: The abstract syntax tree to interpret
            
        Returns:
            The result of the interpretation, if any
        """
        return self.runtime.evaluate(ast)