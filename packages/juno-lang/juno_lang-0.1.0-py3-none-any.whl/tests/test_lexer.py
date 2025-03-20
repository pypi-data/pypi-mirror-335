"""
Tests for the Juno lexer.
"""

import unittest
from juno.lexer import Lexer, TokenType

class TestLexer(unittest.TestCase):
    """Test cases for the Juno lexer."""
    
    def test_empty_source(self):
        """Test lexing an empty source."""
        lexer = Lexer("", "<test>")
        tokens = lexer.scan_tokens()
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)
    
    def test_numbers(self):
        """Test lexing numbers."""
        lexer = Lexer("123 456.789", "<test>")
        tokens = lexer.scan_tokens()
        self.assertEqual(len(tokens), 3)  # 2 numbers + EOF
        self.assertEqual(tokens[0].type, TokenType.NUMBER)
        self.assertEqual(tokens[0].literal, 123)
        self.assertEqual(tokens[1].type, TokenType.NUMBER)
        self.assertEqual(tokens[1].literal, 456.789)
    
    def test_strings(self):
        """Test lexing strings."""
        lexer = Lexer('"Hello, World!"', "<test>")
        tokens = lexer.scan_tokens()
        self.assertEqual(len(tokens), 2)  # 1 string + EOF
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].literal, "Hello, World!")
    
    def test_identifiers_and_keywords(self):
        """Test lexing identifiers and keywords."""
        lexer = Lexer("let x = 5; if (x) { return true; }", "<test>")
        tokens = lexer.scan_tokens()
        self.assertEqual(tokens[0].type, TokenType.LET)
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].lexeme, "x")
        self.assertEqual(tokens[3].type, TokenType.NUMBER)
        self.assertEqual(tokens[5].type, TokenType.IF)
        self.assertEqual(tokens[10].type, TokenType.RETURN)
        self.assertEqual(tokens[11].type, TokenType.TRUE)
    
    def test_operators(self):
        """Test lexing operators."""
        lexer = Lexer("+-*/ == != < <= > >= !", "<test>")
        tokens = lexer.scan_tokens()
        self.assertEqual(tokens[0].type, TokenType.PLUS)
        self.assertEqual(tokens[1].type, TokenType.MINUS)
        self.assertEqual(tokens[2].type, TokenType.STAR)
        self.assertEqual(tokens[3].type, TokenType.SLASH)
        self.assertEqual(tokens[4].type, TokenType.EQUAL_EQUAL)
        self.assertEqual(tokens[5].type, TokenType.BANG_EQUAL)
        self.assertEqual(tokens[6].type, TokenType.LESS)
        self.assertEqual(tokens[7].type, TokenType.LESS_EQUAL)
        self.assertEqual(tokens[8].type, TokenType.GREATER)
        self.assertEqual(tokens[9].type, TokenType.GREATER_EQUAL)
        self.assertEqual(tokens[10].type, TokenType.BANG)
    
    def test_comments(self):
        """Test lexing comments."""
        lexer = Lexer("// This is a comment\nx = 5; /* Multi-line\ncomment */ y = 10;", "<test>")
        tokens = lexer.scan_tokens()
        # Comments should be ignored, so we should have: identifier, equal, number, semicolon, identifier, equal, number, semicolon, EOF
        self.assertEqual(len(tokens), 9)
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].lexeme, "x")
        self.assertEqual(tokens[4].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[4].lexeme, "y")
    
    def test_arrow_operator(self):
        """Test lexing the arrow operator."""
        lexer = Lexer("case 1 => 'one'", "<test>")
        tokens = lexer.scan_tokens()
        self.assertEqual(tokens[0].type, TokenType.CASE)
        self.assertEqual(tokens[1].type, TokenType.NUMBER)
        self.assertEqual(tokens[2].type, TokenType.ARROW)
        self.assertEqual(tokens[3].type, TokenType.STRING)

if __name__ == "__main__":
    unittest.main()