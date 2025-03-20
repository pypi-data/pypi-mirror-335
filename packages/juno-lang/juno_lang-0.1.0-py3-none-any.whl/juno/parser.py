"""
Parser for the Juno programming language.
"""

from juno.lexer import TokenType
from juno.ast import (
    Program, BinaryExpr, UnaryExpr, LiteralExpr, GroupingExpr, 
    VariableExpr, AssignExpr, CallExpr, FunctionDecl, 
    ExpressionStmt, PrintStmt, VarStmt, BlockStmt, 
    IfStmt, WhileStmt, ReturnStmt, MatchStmt, CaseClause,
    TryStmt, AsyncStmt, AwaitExpr
)

class ParseError(Exception):
    """Exception raised for parsing errors."""
    pass

class Parser:
    """
    The Parser class is responsible for converting tokens into an abstract syntax tree.
    """
    
    def __init__(self, tokens, source_name):
        """
        Initialize the parser.
        
        Args:
            tokens (list): A list of Token objects
            source_name (str): The name of the source (file name or "<repl>")
        """
        self.tokens = tokens
        self.source_name = source_name
        self.current = 0
    
    def parse(self):
        """
        Parse the tokens into an abstract syntax tree.
        
        Returns:
            Program: The root node of the abstract syntax tree
        """
        statements = []
        
        while not self._is_at_end():
            statements.append(self._declaration())
        
        return Program(statements)
    
    def _declaration(self):
        """Parse a declaration."""
        try:
            if self._match(TokenType.FUNC):
                return self._function("function")
            if self._match(TokenType.LET, TokenType.VAR):
                return self._var_declaration()
            
            return self._statement()
        except ParseError:
            self._synchronize()
            return None
    
    def _function(self, kind):
        """Parse a function declaration."""
        name = None
        if self._check(TokenType.IDENTIFIER):
            name = self._consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        
        self._consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        
        parameters = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self._error(self._peek(), "Cannot have more than 255 parameters.")
                
                parameters.append(self._consume(TokenType.IDENTIFIER, "Expect parameter name."))
                
                if not self._match(TokenType.COMMA):
                    break
        
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        
        # Parse the function body
        self._consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self._block()
        
        return FunctionDecl(name.lexeme if name else None, parameters, body)
    
    def _var_declaration(self):
        """Parse a variable declaration."""
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        
        initializer = None
        if self._match(TokenType.EQUAL):
            initializer = self._expression()
        
        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return VarStmt(name, initializer)
    
    def _statement(self):
        """Parse a statement."""
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.WHILE):
            return self._while_statement()
        if self._match(TokenType.FOR):
            return self._for_statement()
        if self._match(TokenType.RETURN):
            return self._return_statement()
        if self._match(TokenType.LEFT_BRACE):
            return BlockStmt(self._block())
        if self._match(TokenType.SHOW):
            return self._print_statement()
        if self._match(TokenType.MATCH):
            return self._match_statement()
        if self._match(TokenType.TRY):
            return self._try_statement()
        if self._match(TokenType.ASYNC):
            return self._async_statement()
        
        return self._expression_statement()
    
    def _if_statement(self):
        """Parse an if statement."""
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        
        then_branch = self._statement()
        else_branch = None
        
        if self._match(TokenType.ELSE):
            else_branch = self._statement()
        
        return IfStmt(condition, then_branch, else_branch)
    
    def _while_statement(self):
        """Parse a while statement."""
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self._statement()
        
        return WhileStmt(condition, body)
    
    def _for_statement(self):
        """Parse a for statement."""
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        
        initializer = None
        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.LET, TokenType.VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()
        
        condition = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")
        
        increment = None
        if not self._check(TokenType.RIGHT_PAREN):
            increment = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")
        
        body = self._statement()
        
        # Desugar for loop into a while loop
        if increment is not None:
            body = BlockStmt([body, ExpressionStmt(increment)])
        
        if condition is None:
            condition = LiteralExpr(True)
        
        body = WhileStmt(condition, body)
        
        if initializer is not None:
            body = BlockStmt([initializer, body])
        
        return body
    
    def _return_statement(self):
        """Parse a return statement."""
        keyword = self._previous()
        value = None
        
        if not self._check(TokenType.SEMICOLON):
            value = self._expression()
        
        self._consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return ReturnStmt(keyword, value)
    
    def _print_statement(self):
        """Parse a print statement."""
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'Show'.")
        value = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after value.")
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        
        return PrintStmt(value)
    
    def _match_statement(self):
        """Parse a match statement."""
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'match'.")
        value = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after value.")
        
        self._consume(TokenType.LEFT_BRACE, "Expect '{' before match cases.")
        
        cases = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            if self._match(TokenType.CASE):
                pattern = self._expression()
                self._consume(TokenType.ARROW, "Expect '=>' after case pattern.")
                body = self._expression()
                cases.append(CaseClause(pattern, body))
                
                # Optional semicolon after case
                self._match(TokenType.SEMICOLON)
            else:
                self._error(self._peek(), "Expect 'case' in match statement.")
                break
        
        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after match cases.")
        
        return MatchStmt(value, cases)
    
    def _try_statement(self):
        """Parse a try statement."""
        try_block = self._statement()
        
        # Parse catch clauses
        catch_clauses = []
        while self._match(TokenType.CASE):
            pattern = self._expression()
            self._consume(TokenType.ARROW, "Expect '=>' after case pattern.")
            body = self._statement()
            catch_clauses.append(CaseClause(pattern, body))
        
        return TryStmt(try_block, catch_clauses)
    
    def _async_statement(self):
        """Parse an async statement."""
        body = self._statement()
        return AsyncStmt(body)
    
    def _block(self):
        """Parse a block of statements."""
        statements = []
        
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            statements.append(self._declaration())
        
        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements
    
    def _expression_statement(self):
        """Parse an expression statement."""
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return ExpressionStmt(expr)
    
    def _expression(self):
        """Parse an expression."""
        return self._assignment()
    
    def _assignment(self):
        """Parse an assignment expression."""
        expr = self._or()
        
        if self._match(TokenType.EQUAL):
            equals = self._previous()
            value = self._assignment()
            
            if isinstance(expr, VariableExpr):
                name = expr.name
                return AssignExpr(name, value)
            
            self._error(equals, "Invalid assignment target.")
        
        return expr
    
    def _or(self):
        """Parse an or expression."""
        expr = self._and()
        
        while self._match(TokenType.OR):
            operator = self._previous()
            right = self._and()
            expr = BinaryExpr(expr, operator, right)
        
        return expr
    
    def _and(self):
        """Parse an and expression."""
        expr = self._equality()
        
        while self._match(TokenType.AND):
            operator = self._previous()
            right = self._equality()
            expr = BinaryExpr(expr, operator, right)
        
        return expr
    
    def _equality(self):
        """Parse an equality expression."""
        expr = self._comparison()
        
        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expr = BinaryExpr(expr, operator, right)
        
        return expr
    
    def _comparison(self):
        """Parse a comparison expression."""
        expr = self._term()
        
        while self._match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self._previous()
            right = self._term()
            expr = BinaryExpr(expr, operator, right)
        
        return expr
    
    def _term(self):
        """Parse a term expression."""
        expr = self._factor()
        
        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator = self._previous()
            right = self._factor()
            expr = BinaryExpr(expr, operator, right)
        
        return expr
    
    def _factor(self):
        """Parse a factor expression."""
        expr = self._unary()
        
        while self._match(TokenType.SLASH, TokenType.STAR):
            operator = self._previous()
            right = self._unary()
            expr = BinaryExpr(expr, operator, right)
        
        return expr
    
    def _unary(self):
        """Parse a unary expression."""
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return UnaryExpr(operator, right)
        
        if self._match(TokenType.AWAIT):
            return AwaitExpr(self._unary())
        
        return self._call()
    
    def _call(self):
        """Parse a call expression."""
        expr = self._primary()
        
        while True:
            if self._match(TokenType.LEFT_PAREN):
                expr = self._finish_call(expr)
            elif self._match(TokenType.DOT):
                name = self._consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
                expr = VariableExpr(expr, name)
            else:
                break
        
        return expr
    
    def _finish_call(self, callee):
        """Finish parsing a call expression."""
        arguments = []
        
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self._error(self._peek(), "Cannot have more than 255 arguments.")
                
                arguments.append(self._expression())
                
                if not self._match(TokenType.COMMA):
                    break
        
        paren = self._consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        
        return CallExpr(callee, paren, arguments)
    
    def _primary(self):
        """Parse a primary expression."""
        if self._match(TokenType.FALSE):
            return LiteralExpr(False)
        if self._match(TokenType.TRUE):
            return LiteralExpr(True)
        if self._match(TokenType.NULL):
            return LiteralExpr(None)
        
        if self._match(TokenType.NUMBER, TokenType.STRING):
            return LiteralExpr(self._previous().literal)
        
        if self._match(TokenType.IDENTIFIER):
            return VariableExpr(self._previous())
        
        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return GroupingExpr(expr)
        
        if self._match(TokenType.FUNC):
            return self._function("function")
        
        self._error(self._peek(), "Expect expression.")
    
    def _match(self, *types):
        """
        Check if the current token matches any of the given types.
        
        Args:
            *types: The token types to check
            
        Returns:
            bool: True if the current token matches any of the given types, False otherwise
        """
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        
        return False
    
    def _check(self, token_type):
        """
        Check if the current token is of the given type.
        
        Args:
            token_type (TokenType): The token type to check
            
        Returns:
            bool: True if the current token is of the given type, False otherwise
        """
        if self._is_at_end():
            return False
        return self._peek().type == token_type
    
    def _advance(self):
        """
        Consume the current token and return it.
        
        Returns:
            Token: The consumed token
        """
        if not self._is_at_end():
            self.current += 1
        return self._previous()
    
    def _is_at_end(self):
        """
        Check if we've reached the end of the tokens.
        
        Returns:
            bool: True if we're at the end of the tokens, False otherwise
        """
        return self._peek().type == TokenType.EOF
    
    def _peek(self):
        """
        Look at the current token without consuming it.
        
        Returns:
            Token: The current token
        """
        return self.tokens[self.current]
    
    def _previous(self):
        """
        Get the previous token.
        
        Returns:
            Token: The previous token
        """
        return self.tokens[self.current - 1]
    
    def _consume(self, token_type, message):
        """
        Consume the current token if it's of the given type, otherwise raise an error.
        
        Args:
            token_type (TokenType): The expected token type
            message (str): The error message if the token doesn't match
            
        Returns:
            Token: The consumed token
            
        Raises:
            ParseError: If the current token is not of the expected type
        """
        if self._check(token_type):
            return self._advance()
        
        self._error(self._peek(), message)
    
    def _error(self, token, message):
        """
        Raise a parse error.
        
        Args:
            token (Token): The token that caused the error
            message (str): The error message
            
        Raises:
            ParseError: Always raised with the given message
        """
        if token.type == TokenType.EOF:
            error_msg = f"[{self.source_name}:{token.line}] Error at end: {message}"
        else:
            error_msg = f"[{self.source_name}:{token.line}] Error at '{token.lexeme}': {message}"
        
        raise ParseError(error_msg)
    
    def _synchronize(self):
        """
        Synchronize the parser after an error.
        
        This method skips tokens until it finds a statement boundary.
        """
        self._advance()
        
        while not self._is_at_end():
            if self._previous().type == TokenType.SEMICOLON:
                return
            
            if self._peek().type in (
                TokenType.CLASS,
                TokenType.FUNC,
                TokenType.LET,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.RETURN,
                TokenType.MATCH,
                TokenType.TRY,
                TokenType.ASYNC
            ):
                return
            
            self._advance()