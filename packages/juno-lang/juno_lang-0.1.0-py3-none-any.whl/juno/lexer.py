"""
Lexer for the Juno programming language.
"""

from enum import Enum, auto

class TokenType(Enum):
    """Token types for the Juno language."""
    # Single-character tokens
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()
    COLON = auto()
    
    # One or two character tokens
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    ARROW = auto()
    COLON_EQUAL = auto()
    
    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    
    # Keywords
    AND = auto()
    CASE = auto()
    CLASS = auto()
    ELSE = auto()
    FALSE = auto()
    FOR = auto()
    FUNC = auto()
    IF = auto()
    LET = auto()
    MATCH = auto()
    NULL = auto()
    OR = auto()
    RETURN = auto()
    SUPER = auto()
    THIS = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()
    TRY = auto()
    ASYNC = auto()
    AWAIT = auto()
    SHOW = auto()  # Built-in print function
    
    EOF = auto()

class Token:
    """
    Represents a token in the Juno language.
    """
    
    def __init__(self, token_type, lexeme, literal, line):
        """
        Initialize a token.
        
        Args:
            token_type (TokenType): The type of the token
            lexeme (str): The original text of the token
            literal: The literal value of the token (for strings, numbers, etc.)
            line (int): The line number where the token appears
        """
        self.type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
    
    def __str__(self):
        if self.literal is not None:
            return f"{self.type.name} '{self.lexeme}' {self.literal}"
        return f"{self.type.name} '{self.lexeme}'"
    
    def __repr__(self):
        return self.__str__()

class Lexer:
    """
    The Lexer class is responsible for breaking down the source code into tokens.
    """
    
    # Map of keywords to their token types
    KEYWORDS = {
        "and": TokenType.AND,
        "case": TokenType.CASE,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "func": TokenType.FUNC,
        "if": TokenType.IF,
        "let": TokenType.LET,
        "match": TokenType.MATCH,
        "null": TokenType.NULL,
        "or": TokenType.OR,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE,
        "try": TokenType.TRY,
        "async": TokenType.ASYNC,
        "await": TokenType.AWAIT,
        "Show": TokenType.SHOW,  # Built-in print function
    }
    
    def __init__(self, source, source_name):
        """
        Initialize the lexer.
        
        Args:
            source (str): The source code to tokenize
            source_name (str): The name of the source (file name or "<repl>")
        """
        self.source = source
        self.source_name = source_name
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
    
    def scan_tokens(self):
        """
        Scan the source code and return a list of tokens.
        
        Returns:
            list: A list of Token objects
        """
        while not self._is_at_end():
            # We are at the beginning of the next lexeme
            self.start = self.current
            self._scan_token()
        
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens
    
    def _scan_token(self):
        """Scan a single token."""
        c = self._advance()
        
        if c == '(':
            self._add_token(TokenType.LEFT_PAREN)
        elif c == ')':
            self._add_token(TokenType.RIGHT_PAREN)
        elif c == '{':
            self._add_token(TokenType.LEFT_BRACE)
        elif c == '}':
            self._add_token(TokenType.RIGHT_BRACE)
        elif c == '[':
            self._add_token(TokenType.LEFT_BRACKET)
        elif c == ']':
            self._add_token(TokenType.RIGHT_BRACKET)
        elif c == ',':
            self._add_token(TokenType.COMMA)
        elif c == '.':
            self._add_token(TokenType.DOT)
        elif c == '-':
            self._add_token(TokenType.ARROW if self._match('>') else TokenType.MINUS)
        elif c == '+':
            self._add_token(TokenType.PLUS)
        elif c == ';':
            self._add_token(TokenType.SEMICOLON)
        elif c == '*':
            self._add_token(TokenType.STAR)
        elif c == '=':
            if self._match('='):
                self._add_token(TokenType.EQUAL_EQUAL)
            elif self._match('>'):
                self._add_token(TokenType.ARROW)
            else:
                self._add_token(TokenType.EQUAL)
        elif c == '!':
            self._add_token(TokenType.BANG_EQUAL if self._match('=') else TokenType.BANG)
        elif c == '<':
            self._add_token(TokenType.LESS_EQUAL if self._match('=') else TokenType.LESS)
        elif c == '>':
            self._add_token(TokenType.GREATER_EQUAL if self._match('=') else TokenType.GREATER)
        elif c == ':':
            self._add_token(TokenType.COLON_EQUAL if self._match('=') else TokenType.COLON)
        elif c == '&' and self._match('&'):
            self._add_token(TokenType.AND)
        elif c == '|' and self._match('|'):
            self._add_token(TokenType.OR)
        # Handle whitespace
        elif c in ' \r\t':
            pass  # Ignore whitespace
        elif c == '\n':
            self.line += 1
        # Handle comments
        elif c == '/':
            if self._match('/'):
                # A comment goes until the end of the line
                while self._peek() != '\n' and not self._is_at_end():
                    self._advance()
            elif self._match('*'):
                # Multi-line comment
                self._multiline_comment()
            else:
                self._add_token(TokenType.SLASH)
        # String literals
        elif c == '"':
            self._string()
        # Number literals and identifiers
        else:
            if self._is_digit(c):
                self._number()
            elif self._is_alpha(c):
                self._identifier()
            else:
                self._error(f"Unexpected character: {c}")
    
    def _multiline_comment(self):
        """Handle multi-line comments."""
        nesting = 1
        while nesting > 0 and not self._is_at_end():
            if self._peek() == '\n':
                self.line += 1
            
            if self._peek() == '/' and self._peek_next() == '*':
                self._advance()  # Consume '/'
                self._advance()  # Consume '*'
                nesting += 1
            elif self._peek() == '*' and self._peek_next() == '/':
                self._advance()  # Consume '*'
                self._advance()  # Consume '/'
                nesting -= 1
            else:
                self._advance()
        
        if nesting > 0:
            self._error("Unterminated multi-line comment.")
    
    def _identifier(self):
        """Handle identifiers and keywords."""
        while self._is_alpha_numeric(self._peek()):
            self._advance()
        
        # See if the identifier is a reserved word
        text = self.source[self.start:self.current]
        token_type = self.KEYWORDS.get(text, TokenType.IDENTIFIER)
        
        self._add_token(token_type)
    
    def _number(self):
        """Handle number literals."""
        while self._is_digit(self._peek()):
            self._advance()
        
        # Look for a decimal part
        if self._peek() == '.' and self._is_digit(self._peek_next()):
            # Consume the "."
            self._advance()
            
            while self._is_digit(self._peek()):
                self._advance()
        
        value = float(self.source[self.start:self.current])
        # Convert to int if it's a whole number
        if value.is_integer():
            value = int(value)
            
        self._add_token(TokenType.NUMBER, value)
    
    def _string(self):
        """Handle string literals."""
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == '\n':
                self.line += 1
            self._advance()
        
        if self._is_at_end():
            self._error("Unterminated string.")
            return
        
        # The closing "
        self._advance()
        
        # Trim the surrounding quotes
        value = self.source[self.start + 1:self.current - 1]
        self._add_token(TokenType.STRING, value)
    
    def _match(self, expected):
        """
        Check if the current character matches the expected character.
        
        Args:
            expected (str): The expected character
            
        Returns:
            bool: True if the current character matches, False otherwise
        """
        if self._is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        
        self.current += 1
        return True
    
    def _peek(self):
        """
        Look at the current character without consuming it.
        
        Returns:
            str: The current character, or '\0' if at the end of the source
        """
        if self._is_at_end():
            return '\0'
        return self.source[self.current]
    
    def _peek_next(self):
        """
        Look at the next character without consuming it.
        
        Returns:
            str: The next character, or '\0' if at the end of the source
        """
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]
    
    def _is_alpha(self, c):
        """
        Check if a character is alphabetic.
        
        Args:
            c (str): The character to check
            
        Returns:
            bool: True if the character is alphabetic, False otherwise
        """
        return ('a' <= c <= 'z') or ('A' <= c <= 'Z') or c == '_'
    
    def _is_alpha_numeric(self, c):
        """
        Check if a character is alphanumeric.
        
        Args:
            c (str): The character to check
            
        Returns:
            bool: True if the character is alphanumeric, False otherwise
        """
        return self._is_alpha(c) or self._is_digit(c)
    
    def _is_digit(self, c):
        """
        Check if a character is a digit.
        
        Args:
            c (str): The character to check
            
        Returns:
            bool: True if the character is a digit, False otherwise
        """
        return '0' <= c <= '9'
    
    def _is_at_end(self):
        """
        Check if we've reached the end of the source.
        
        Returns:
            bool: True if we're at the end of the source, False otherwise
        """
        return self.current >= len(self.source)
    
    def _advance(self):
        """
        Consume the current character and return it.
        
        Returns:
            str: The consumed character
        """
        c = self.source[self.current]
        self.current += 1
        return c
    
    def _add_token(self, token_type, literal=None):
        """
        Add a token to the list of tokens.
        
        Args:
            token_type (TokenType): The type of the token
            literal: The literal value of the token (for strings, numbers, etc.)
        """
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))
    
    def _error(self, message):
        """
        Raise an error with the given message.
        
        Args:
            message (str): The error message
            
        Raises:
            SyntaxError: Always raised with the given message
        """
        raise SyntaxError(f"[{self.source_name}:{self.line}] Error: {message}")