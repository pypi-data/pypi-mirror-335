"""
Abstract Syntax Tree (AST) nodes for the Juno programming language.
"""

class Node:
    """Base class for all AST nodes."""
    pass

# Program node

class Program(Node):
    """Represents a complete program."""
    
    def __init__(self, statements):
        """
        Initialize a program.
        
        Args:
            statements (list): A list of statement nodes
        """
        self.statements = statements
    
    def __str__(self):
        return f"Program({len(self.statements)} statements)"

# Expression nodes

class Expr(Node):
    """Base class for all expression nodes."""
    pass

class BinaryExpr(Expr):
    """Represents a binary expression (e.g., a + b)."""
    
    def __init__(self, left, operator, right):
        """
        Initialize a binary expression.
        
        Args:
            left (Expr): The left operand
            operator (Token): The operator token
            right (Expr): The right operand
        """
        self.left = left
        self.operator = operator
        self.right = right
    
    def __str__(self):
        return f"Binary({self.left}, {self.operator.lexeme}, {self.right})"

class UnaryExpr(Expr):
    """Represents a unary expression (e.g., -a, !b)."""
    
    def __init__(self, operator, right):
        """
        Initialize a unary expression.
        
        Args:
            operator (Token): The operator token
            right (Expr): The operand
        """
        self.operator = operator
        self.right = right
    
    def __str__(self):
        return f"Unary({self.operator.lexeme}, {self.right})"

class LiteralExpr(Expr):
    """Represents a literal value (e.g., 123, "hello")."""
    
    def __init__(self, value):
        """
        Initialize a literal expression.
        
        Args:
            value: The literal value
        """
        self.value = value
    
    def __str__(self):
        return f"Literal({self.value})"

class GroupingExpr(Expr):
    """Represents a grouping expression (e.g., (a + b))."""
    
    def __init__(self, expression):
        """
        Initialize a grouping expression.
        
        Args:
            expression (Expr): The expression inside the grouping
        """
        self.expression = expression
    
    def __str__(self):
        return f"Grouping({self.expression})"

class VariableExpr(Expr):
    """Represents a variable reference."""
    
    def __init__(self, name, object=None):
        """
        Initialize a variable expression.
        
        Args:
            name (Token): The variable name token
            object (Expr, optional): The object if this is a property access
        """
        self.name = name
        self.object = object
    
    def __str__(self):
        if self.object:
            return f"Get({self.object}, {self.name.lexeme})"
        return f"Variable({self.name.lexeme})"

class AssignExpr(Expr):
    """Represents an assignment expression (e.g., a = b)."""
    
    def __init__(self, name, value):
        """
        Initialize an assignment expression.
        
        Args:
            name (Token): The variable name token
            value (Expr): The value to assign
        """
        self.name = name
        self.value = value
    
    def __str__(self):
        return f"Assign({self.name.lexeme}, {self.value})"

class CallExpr(Expr):
    """Represents a function call expression (e.g., foo(1, 2))."""
    
    def __init__(self, callee, paren, arguments):
        """
        Initialize a call expression.
        
        Args:
            callee (Expr): The function to call
            paren (Token): The closing parenthesis token (for error reporting)
            arguments (list): A list of argument expressions
        """
        self.callee = callee
        self.paren = paren
        self.arguments = arguments
    
    def __str__(self):
        return f"Call({self.callee}, {len(self.arguments)} args)"

class AwaitExpr(Expr):
    """Represents an await expression (e.g., await foo())."""
    
    def __init__(self, expression):
        """
        Initialize an await expression.
        
        Args:
            expression (Expr): The expression to await
        """
        self.expression = expression
    
    def __str__(self):
        return f"Await({self.expression})"

# Statement nodes

class Stmt(Node):
    """Base class for all statement nodes."""
    pass

class ExpressionStmt(Stmt):
    """Represents an expression statement."""
    
    def __init__(self, expression):
        """
        Initialize an expression statement.
        
        Args:
            expression (Expr): The expression
        """
        self.expression = expression
    
    def __str__(self):
        return f"ExprStmt({self.expression})"

class PrintStmt(Stmt):
    """Represents a print statement (Show(...))."""
    
    def __init__(self, expression):
        """
        Initialize a print statement.
        
        Args:
            expression (Expr): The expression to print
        """
        self.expression = expression
    
    def __str__(self):
        return f"Print({self.expression})"

class VarStmt(Stmt):
    """Represents a variable declaration statement."""
    
    def __init__(self, name, initializer):
        """
        Initialize a variable declaration statement.
        
        Args:
            name (Token): The variable name token
            initializer (Expr): The initializer expression, or None
        """
        self.name = name
        self.initializer = initializer
    
    def __str__(self):
        return f"Var({self.name.lexeme}, {self.initializer})"

class BlockStmt(Stmt):
    """Represents a block statement."""
    
    def __init__(self, statements):
        """
        Initialize a block statement.
        
        Args:
            statements (list): A list of statement nodes
        """
        self.statements = statements
    
    def __str__(self):
        return f"Block({len(self.statements)} statements)"

class IfStmt(Stmt):
    """Represents an if statement."""
    
    def __init__(self, condition, then_branch, else_branch):
        """
        Initialize an if statement.
        
        Args:
            condition (Expr): The condition expression
            then_branch (Stmt): The statement to execute if the condition is true
            else_branch (Stmt): The statement to execute if the condition is false, or None
        """
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    
    def __str__(self):
        return f"If({self.condition}, {self.then_branch}, {self.else_branch})"

class WhileStmt(Stmt):
    """Represents a while statement."""
    
    def __init__(self, condition, body):
        """
        Initialize a while statement.
        
        Args:
            condition (Expr): The condition expression
            body (Stmt): The body statement
        """
        self.condition = condition
        self.body = body
    
    def __str__(self):
        return f"While({self.condition}, {self.body})"

class FunctionDecl(Stmt):
    """Represents a function declaration."""
    
    def __init__(self, name, params, body):
        """
        Initialize a function declaration.
        
        Args:
            name (str): The function name
            params (list): A list of parameter tokens
            body (list): A list of statement nodes
        """
        self.name = name
        self.params = params
        self.body = body
    
    def __str__(self):
        return f"Function({self.name}, {len(self.params)} params)"

class ReturnStmt(Stmt):
    """Represents a return statement."""
    
    def __init__(self, keyword, value):
        """
        Initialize a return statement.
        
        Args:
            keyword (Token): The return keyword token (for error reporting)
            value (Expr): The return value expression, or None
        """
        self.keyword = keyword
        self.value = value
    
    def __str__(self):
        return f"Return({self.value})"

class MatchStmt(Stmt):
    """Represents a match statement."""
    
    def __init__(self, value, cases):
        """
        Initialize a match statement.
        
        Args:
            value (Expr): The value to match against
            cases (list): A list of CaseClause nodes
        """
        self.value = value
        self.cases = cases
    
    def __str__(self):
        return f"Match({self.value}, {len(self.cases)} cases)"

class CaseClause(Node):
    """Represents a case clause in a match statement."""
    
    def __init__(self, pattern, body):
        """
        Initialize a case clause.
        
        Args:
            pattern (Expr): The pattern to match against
            body (Expr or Stmt): The body to execute if the pattern matches
        """
        self.pattern = pattern
        self.body = body
    
    def __str__(self):
        return f"Case({self.pattern}, {self.body})"

class TryStmt(Stmt):
    """Represents a try statement."""
    
    def __init__(self, try_block, catch_clauses):
        """
        Initialize a try statement.
        
        Args:
            try_block (Stmt): The try block
            catch_clauses (list): A list of CaseClause nodes for error handling
        """
        self.try_block = try_block
        self.catch_clauses = catch_clauses
    
    def __str__(self):
        return f"Try({self.try_block}, {len(self.catch_clauses)} catch clauses)"

class AsyncStmt(Stmt):
    """Represents an async statement."""
    
    def __init__(self, body):
        """
        Initialize an async statement.
        
        Args:
            body (Stmt): The body statement
        """
        self.body = body
    
    def __str__(self):
        return f"Async({self.body})"