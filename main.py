from typing import Dict, List
from enum import Enum, auto
from pprint import pprint
import sys


class LexException(Exception):
    pass


class ParseException(Exception):
    pass


class TokenType(Enum):
    LSQUIRLY = auto()
    RSQUIRLY = auto()
    COMMA = auto()
    COLON = auto()
    STRING = auto()
    NUMBER = auto()
    EOF = auto()    # EOF just indicates the end of the token stream


# Any discrete part of the language that can be considered a separate thing
# in of itself. For example, it may be a keyword, an operator, or a string or
# number, or punctuation like braces or semicolons.
class Token:
    def __init__(self, tok_type: TokenType, lexeme: str):
        self.tok_type = tok_type
        self.lexeme = lexeme

    def __str__(self):
        return f"({self.tok_type}, {self.lexeme})"

    def __repr__(self):
        return f"(type: {self.tok_type}, lexeme: {self.lexeme})"


# The lexer takes the input string and from that, gives you a list of tokens.
class Lexer:
    def __init__(self, source: str):
        self.source = source    # The string which we're forming tokens out of
        self.i = 0      # The index in the source where the lexer's at currently
        self.tokens: List[Token] = []
        pass

    # Check if a character is a digit.
    def is_digit(self, char: str) -> bool:
        return "0" <= char <= "9"

    # Check if we've reached the end.
    def is_at_end(self):
        return self.i >= len(self.source)

    def consume_whitespace(self):
        while self.source[self.i] == " ":
            self.i += 1

    def make_token(self, tok_type: TokenType, lexeme: str):
        self.tokens.append(Token(tok_type, lexeme))

    def handle_string(self):
        self.i += 1  # consume the "
        key = ""

        # grab the string content
        while not self.is_at_end() and self.source[self.i] != "\"" :
            key += self.source[self.i]
            self.i += 1

        if self.is_at_end():
            raise LexException("Unterminated string")

        self.i += 1     # consume the last "
        self.make_token(TokenType.STRING, "\"" + key + "\"")

    def handle_number(self):
        key = ""
        while self.is_digit(self.source[self.i]):
            if self.is_at_end():
                raise LexException("json input ended abruptly")

            key += self.source[self.i]
            self.i += 1

        self.make_token(TokenType.NUMBER, key)

    def consume(self):
        self.consume_whitespace()

        char = self.source[self.i]
        match char:
            case "{":
                self.make_token(TokenType.LSQUIRLY, "{")
                self.i += 1
            case "}":
                self.make_token(TokenType.RSQUIRLY, "}")
                self.i += 1
            case ",":
                self.make_token(TokenType.COMMA, ",")
                self.i += 1
            case ":":
                self.make_token(TokenType.COLON, ":")
                self.i += 1
            case "\"":
                self.handle_string()
            case _ if self.is_digit(char):
                self.handle_number()
            case _:
                raise LexException(f"Unexpected character: {char}")

    def lex(self) -> List[Token]:
        while self.i < len(self.source):
            self.consume()

        self.make_token(TokenType.EOF, "")

        return self.tokens


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.i = 0
        self.result: Dict[str, str | float] = {}

    def consume(self, expected: str):
        if self.is_at_end():
            raise ParseException("json input ended without \"}\"")

        found = self.curr().lexeme
        if found != expected:
            raise ParseException(f"Expected {expected} but got {found}")

        self.i += 1

    def match(self, expected: str) -> bool:
        if self.is_at_end():
            raise ParseException("json input ended without \"}\"")

        found = self.curr().lexeme
        if found != expected:
            return False

        self.i += 1
        return True

    def is_at_end(self) -> bool:
        return self.curr().tok_type == TokenType.EOF

    def curr(self) -> Token:
        return self.tokens[self.i]

    def next(self) -> Token | None:
        if self.is_at_end():
            return None

        return self.tokens[self.i + 1]

    def key(self) -> str:
        if self.is_at_end():
            raise ParseException("Expected string")

        curr = self.curr()

        # In json, only strings can be keys
        if curr.tok_type != TokenType.STRING:
            raise ParseException("Expected string")

        key = curr.lexeme[1:-1]
        self.i += 1
        return key

    def value(self):
        if self.is_at_end():
            raise ParseException("Expected a value for the corresponding key")

        value = 0
        curr = self.curr()

        # For now, only strings and numbers are supported by the parser
        match curr.tok_type:
            case TokenType.STRING:
                value = curr.lexeme[1:-1]
            case TokenType.NUMBER:
                value = float(curr.lexeme)
            case _:
                raise ParseException("Expected string or number")

        self.i += 1
        return value

    def pair(self):
        key = self.key()
        self.consume(":")
        value = self.value()

        # After grabbing the key and value, set it in the result dict
        self.result[key] = value

    def json(self):
        # Accept empty strings
        if self.is_at_end():
            return

        self.consume("{")

        # Accept {}
        if self.match("}"):
            return

        # The structure of the while loop disallows trailing commas.
        # This is because the json spec doesn't allow trailing commas itself.
        while not self.is_at_end():
            self.pair()

            if self.match("}"):
                return

            self.consume(",")

        raise ParseException("json input ended without \"}\"")

    def parse(self) -> Dict[str, str | float]:
        self.json()

        return self.result


def main():
    try:
        json = input()

        lexer = Lexer(json)

        try:
            tokens = lexer.lex()
        except LexException as e:
            print(f"\033[31mlexer error:\033[0m {str(e)}", file=sys.stderr)
            exit(1)

        parser = Parser(tokens)

        try:
            result = parser.parse()
        except ParseException as e:
            print(f"\033[31mparse error:\033[0m {str(e)}", file=sys.stderr)
            exit(1)

        pprint(result)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
