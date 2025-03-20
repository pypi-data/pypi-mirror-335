"""
Runtime environment for the Juno programming language.
"""

import time
import asyncio
from juno.ast import (
    Program, BinaryExpr, UnaryExpr, LiteralExpr, GroupingExpr, 
    VariableExpr, AssignExpr, CallExpr, FunctionDecl, 
    ExpressionStmt, PrintStmt, VarStmt, BlockStmt, 
    IfStmt, WhileStmt, ReturnStmt, MatchStmt, CaseClause,
    TryStmt, AsyncStmt, AwaitExpr
)
from juno.lexer import TokenType

class RuntimeError(Exception):
    """Exception raised for runtime errors."""
    pass

class Return(Exception):
    """Exception used for handling return statements."""
    
    def __init__(self, value):
        """
        Initialize a return exception.
        
        Args:
            value: The return value
        """
        self.value = value
        super().__init__(str(value))

class Environment:
    """
    Represents a lexical environment for variable storage.
    """
    
    def __init__(self, enclosing=None):
        """
        Initialize an environment.
        
        Args:
            enclosing (Environment, optional): The enclosing environment
        """
        self.values = {}
        self.enclosing = enclosing
    
    def define(self, name, value):
        """
        Define a variable in the current environment.
        
        Args:
            name (str): The variable name
            value: The variable value
        """
        self.values[name] = value
    
    def get(self, name):
        """
        Get a variable value from the environment.
        
        Args:
            name (str): The variable name
            
        Returns:
            The variable value
            
        Raises:
            RuntimeError: If the variable is not defined
        """
        if name in self.values:
            return self.values[name]
        
        if self.enclosing:
            return self.enclosing.get(name)
        
        raise RuntimeError(f"Undefined variable '{name}'.")
    
    def assign(self, name, value):
        """
        Assign a new value to an existing variable.
        
        Args:
            name (str): The variable name
            value: The new value
            
        Raises:
            RuntimeError: If the variable is not defined
        """
        if name in self.values:
            self.values[name] = value
            return
        
        if self.enclosing:
            self.enclosing.assign(name, value)
            return
        
        raise RuntimeError(f"Undefined variable '{name}'.")

class JunoFunction:
    """
    Represents a Juno function.
    """
    
    def __init__(self, declaration, closure, is_async=False):
        """
        Initialize a function.
        
        Args:
            declaration (FunctionDecl): The function declaration
            closure (Environment): The lexical environment where the function was defined
            is_async (bool): Whether the function is asynchronous
        """
        self.declaration = declaration
        self.closure = closure
        self.is_async = is_async
    
    def call(self, interpreter, arguments):
        """
        Call the function with the given arguments.
        
        Args:
            interpreter: The interpreter
            arguments (list): The argument values
            
        Returns:
            The return value of the function
            
        Raises:
            Return: To handle return statements
        """
        environment = Environment(self.closure)
        
        # Bind parameters to arguments
        for i, param in enumerate(self.declaration.params):
            if i < len(arguments):
                environment.define(param.lexeme, arguments[i])
            else:
                environment.define(param.lexeme, None)
        
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as r:
            return r.value
        
        return None
    
    async def call_async(self, interpreter, arguments):
        """
        Call the function asynchronously with the given arguments.
        
        Args:
            interpreter: The interpreter
            arguments (list): The argument values
            
        Returns:
            The return value of the function
            
        Raises:
            Return: To handle return statements
        """
        environment = Environment(self.closure)
        
        # Bind parameters to arguments
        for i, param in enumerate(self.declaration.params):
            if i < len(arguments):
                environment.define(param.lexeme, arguments[i])
            else:
                environment.define(param.lexeme, None)
        
        try:
            await interpreter.execute_block_async(self.declaration.body, environment)
        except Return as r:
            return r.value
        
        return None
    
    def __str__(self):
        if self.declaration.name:
            return f"<function {self.declaration.name}>"
        return "<anonymous function>"

class Runtime:
    """
    Runtime environment for executing Juno code.
    """
    
    def __init__(self):
        """Initialize the runtime environment."""
        self.globals = Environment()
        self.environment = self.globals
        self.locals = {}
        
        # Define native functions
        self._define_natives()
        
        # For async support
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def _define_natives(self):
        """Define native functions in the global environment."""
        # clock() - returns the current time in seconds
        self.globals.define("clock", lambda: time.time())
        
        # sleep(seconds) - sleeps for the given number of seconds
        self.globals.define("sleep", lambda seconds: time.sleep(seconds))
        
        # len(obj) - returns the length of a string or list
        self.globals.define("len", lambda obj: len(obj) if isinstance(obj, (str, list)) else 0)
        
        # str(obj) - converts an object to a string
        self.globals.define("str", lambda obj: str(obj))
        
        # num(obj) - converts an object to a number
        def num(obj):
            try:
                return float(obj)
            except (ValueError, TypeError):
                return 0
        self.globals.define("num", num)
        
        # print(obj) - prints an object to the console
        self.globals.define("print", lambda obj: print(obj))
    
    def evaluate(self, expr):
        """
        Evaluate an expression.
        
        Args:
            expr: The expression to evaluate
            
        Returns:
            The result of the evaluation
        """
        # Program
        if isinstance(expr, Program):
            result = None
            for stmt in expr.statements:
                result = self.evaluate(stmt)
            return result
        
        # Expressions
        elif isinstance(expr, BinaryExpr):
            return self._evaluate_binary(expr)
        elif isinstance(expr, UnaryExpr):
            return self._evaluate_unary(expr)
        elif isinstance(expr, LiteralExpr):
            return expr.value
        elif isinstance(expr, GroupingExpr):
            return self.evaluate(expr.expression)
        elif isinstance(expr, VariableExpr):
            return self._evaluate_variable(expr)
        elif isinstance(expr, AssignExpr):
            return self._evaluate_assign(expr)
        elif isinstance(expr, CallExpr):
            return self._evaluate_call(expr)
        elif isinstance(expr, AwaitExpr):
            return self._evaluate_await(expr)
        
        # Statements
        elif isinstance(expr, ExpressionStmt):
            return self.evaluate(expr.expression)
        elif isinstance(expr, PrintStmt):
            value = self.evaluate(expr.expression)
            print(value)
            return None
        elif isinstance(expr, VarStmt):
            return self._execute_var(expr)
        elif isinstance(expr, BlockStmt):
            return self._execute_block(expr)
        elif isinstance(expr, IfStmt):
            return self._execute_if(expr)
        elif isinstance(expr, WhileStmt):
            return self._execute_while(expr)
        elif isinstance(expr, FunctionDecl):
            return self._execute_function(expr)
        elif isinstance(expr, ReturnStmt):
            return self._execute_return(expr)
        elif isinstance(expr, MatchStmt):
            return self._execute_match(expr)
        elif isinstance(expr, TryStmt):
            return self._execute_try(expr)
        elif isinstance(expr, AsyncStmt):
            return self._execute_async(expr)
        
        raise RuntimeError(f"Unknown expression type: {type(expr)}")
    
    def _evaluate_binary(self, expr):
        """Evaluate a binary expression."""
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        
        if expr.operator.type == TokenType.PLUS:
            # String concatenation
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            # Number addition
            return left + right
        elif expr.operator.type == TokenType.MINUS:
            self._check_number_operands(expr.operator, left, right)
            return left - right
        elif expr.operator.type == TokenType.STAR:
            self._check_number_operands(expr.operator, left, right)
            return left * right
        elif expr.operator.type == TokenType.SLASH:
            self._check_number_operands(expr.operator, left, right)
            if right == 0:
                raise RuntimeError("Division by zero.")
            return left / right
        elif expr.operator.type == TokenType.GREATER:
            self._check_number_operands(expr.operator, left, right)
            return left > right
        elif expr.operator.type == TokenType.GREATER_EQUAL:
            self._check_number_operands(expr.operator, left, right)
            return left >= right
        elif expr.operator.type == TokenType.LESS:
            self._check_number_operands(expr.operator, left, right)
            return left < right
        elif expr.operator.type == TokenType.LESS_EQUAL:
            self._check_number_operands(expr.operator, left, right)
            return left <= right
        elif expr.operator.type == TokenType.EQUAL_EQUAL:
            return self._is_equal(left, right)
        elif expr.operator.type == TokenType.BANG_EQUAL:
            return not self._is_equal(left, right)
        elif expr.operator.type == TokenType.AND:
            return bool(left) and bool(right)
        elif expr.operator.type == TokenType.OR:
            return bool(left) or bool(right)
        
        # Unreachable
        return None
    
    def _evaluate_unary(self, expr):
        """Evaluate a unary expression."""
        right = self.evaluate(expr.right)
        
        if expr.operator.type == TokenType.MINUS:
            self._check_number_operand(expr.operator, right)
            return -right
        elif expr.operator.type == TokenType.BANG:
            return not self._is_truthy(right)
        
        # Unreachable
        return None
    
    def _evaluate_variable(self, expr):
        """Evaluate a variable expression."""
        if expr.object:
            obj = self.evaluate(expr.object)
            # Handle property access
            if hasattr(obj, expr.name.lexeme):
                return getattr(obj, expr.name.lexeme)
            raise RuntimeError(f"Undefined property '{expr.name.lexeme}'.")
        
        return self.environment.get(expr.name.lexeme)
    
    def _evaluate_assign(self, expr):
        """Evaluate an assignment expression."""
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name.lexeme, value)
        return value
    
    def _evaluate_call(self, expr):
        """Evaluate a call expression."""
        callee = self.evaluate(expr.callee)
        
        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))
        
        if not callable(callee) and not isinstance(callee, JunoFunction):
            raise RuntimeError("Can only call functions and classes.")
        
        # Check arity
        if isinstance(callee, JunoFunction):
            if len(arguments) != len(callee.declaration.params):
                raise RuntimeError(f"Expected {len(callee.declaration.params)} arguments but got {len(arguments)}.")
            
            if callee.is_async:
                # Run async function in the event loop
                return self.loop.run_until_complete(callee.call_async(self, arguments))
            
            return callee.call(self, arguments)
        
        # Native function
        return callee(*arguments)
    
    def _evaluate_await(self, expr):
        """Evaluate an await expression."""
        value = self.evaluate(expr.expression)
        
        if asyncio.iscoroutine(value):
            return self.loop.run_until_complete(value)
        
        return value
    
    def _execute_var(self, stmt):
        """Execute a variable declaration statement."""
        value = None
        if stmt.initializer:
            value = self.evaluate(stmt.initializer)
        
        self.environment.define(stmt.name.lexeme, value)
        return None
    
    def _execute_block(self, stmt):
        """Execute a block statement."""
        previous = self.environment
        try:
            self.environment = Environment(previous)
            
            for statement in stmt.statements:
                self.evaluate(statement)
            
            return None
        finally:
            self.environment = previous
    
    def execute_block(self, statements, environment):
        """
        Execute a block of statements in the given environment.
        
        Args:
            statements (list): A list of statement nodes
            environment (Environment): The environment to use
        """
        previous = self.environment
        try:
            self.environment = environment
            
            for statement in statements:
                self.evaluate(statement)
        finally:
            self.environment = previous
    
    async def execute_block_async(self, statements, environment):
        """
        Execute a block of statements asynchronously in the given environment.
        
        Args:
            statements (list): A list of statement nodes
            environment (Environment): The environment to use
        """
        previous = self.environment
        try:
            self.environment = environment
            
            for statement in statements:
                if isinstance(statement, AsyncStmt):
                    await self._execute_async(statement)
                elif isinstance(statement, ExpressionStmt) and isinstance(statement.expression, AwaitExpr):
                    await self._evaluate_await(statement.expression)
                else:
                    self.evaluate(statement)
        finally:
            self.environment = previous
    
    def _execute_if(self, stmt):
        """Execute an if statement."""
        if self._is_truthy(self.evaluate(stmt.condition)):
            return self.evaluate(stmt.then_branch)
        elif stmt.else_branch:
            return self.evaluate(stmt.else_branch)
        
        return None
    
    def _execute_while(self, stmt):
        """Execute a while statement."""
        while self._is_truthy(self.evaluate(stmt.condition)):
            self.evaluate(stmt.body)
        
        return None
    
    def _execute_function(self, stmt):
        """Execute a function declaration."""
        function = JunoFunction(stmt, self.environment)
        
        if stmt.name:
            self.environment.define(stmt.name, function)
        
        return function
    
    def _execute_return(self, stmt):
        """Execute a return statement."""
        value = None
        if stmt.value:
            value = self.evaluate(stmt.value)
        
        raise Return(value)
    
    def _execute_match(self, stmt):
        """Execute a match statement."""
        value = self.evaluate(stmt.value)
        
        for case in stmt.cases:
            pattern = self.evaluate(case.pattern)
            
            # Special case for wildcard pattern
            if isinstance(pattern, VariableExpr) and pattern.name.lexeme == "_":
                return self.evaluate(case.body)
            
            if self._is_equal(value, pattern):
                return self.evaluate(case.body)
        
        return None
    
    def _execute_try(self, stmt):
        """Execute a try statement."""
        try:
            return self.evaluate(stmt.try_block)
        except Exception as e:
            for case in stmt.catch_clauses:
                pattern = self.evaluate(case.pattern)
                
                # Special case for wildcard pattern
                if isinstance(pattern, VariableExpr) and pattern.name.lexeme == "_":
                    return self.evaluate(case.body)
                
                # Match by exception type
                if isinstance(pattern, VariableExpr):
                    if pattern.name.lexeme == type(e).__name__:
                        return self.evaluate(case.body)
            
            # Re-raise if no matching catch clause
            raise
    
    def _execute_async(self, stmt):
        """Execute an async statement."""
        # Create an async function and immediately call it
        async_function = JunoFunction(
            FunctionDecl(None, [], stmt.body.statements if isinstance(stmt.body, BlockStmt) else [stmt.body]),
            self.environment,
            is_async=True
        )
        
        return self.loop.run_until_complete(async_function.call_async(self, []))
    
    def _is_truthy(self, value):
        """
        Determine if a value is truthy.
        
        Args:
            value: The value to check
            
        Returns:
            bool: True if the value is truthy, False otherwise
        """
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        
        return True
    
    def _is_equal(self, a, b):
        """
        Determine if two values are equal.
        
        Args:
            a: The first value
            b: The second value
            
        Returns:
            bool: True if the values are equal, False otherwise
        """
        if a is None and b is None:
            return True
        if a is None:
            return False
        
        return a == b
    
    def _check_number_operand(self, operator, operand):
        """
        Check if an operand is a number.
        
        Args:
            operator: The operator token
            operand: The operand to check
            
        Raises:
            RuntimeError: If the operand is not a number
        """
        if isinstance(operand, (int, float)):
            return
        
        raise RuntimeError(f"Operand must be a number for operator '{operator.lexeme}'.")
    
    def _check_number_operands(self, operator, left, right):
        """
        Check if both operands are numbers.
        
        Args:
            operator: The operator token
            left: The left operand
            right: The right operand
            
        Raises:
            RuntimeError: If either operand is not a number
        """
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return
        
        raise RuntimeError(f"Operands must be numbers for operator '{operator.lexeme}'.")