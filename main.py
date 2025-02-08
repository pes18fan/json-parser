from typing import Dict, List
from enum import Enum, auto
from pprint import pprint


class TokenType(Enum):
    COMMA = auto()
    COLON = auto()
    STRING = auto()
    NUMBER = auto()


class Token:
    def __init__(self, tok_type: TokenType, lexeme: str):
        self.tok_type = tok_type
        self.lexeme = lexeme

    def __str__(self):
        return f"({self.tok_type}, {self.lexeme})"

    def __repr__(self):
        return f"(type: {self.tok_type}, lexeme: {self.lexeme})"


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.i = 0
        self.tokens: List[Token] = []
        pass

    def is_digit(self, char: str) -> bool:
        return "0" <= char <= "9"

    def consume_whitespace(self):
        while self.source[self.i] == " ":
            self.i += 1

    def make_token(self, tok_type: TokenType, lexeme: str):
        self.tokens.append(Token(tok_type, lexeme))

    def handle_string(self):
        self.i += 1  # consume the "
        key = ""

        # grab the string content
        while self.i < len(self.source) and self.source[self.i] != "\"" :
            key += self.source[self.i]
            self.i += 1

        if self.i >= len(self.source):
            raise Exception("Unterminated string")

        self.i += 1     # consume the last "
        self.make_token(TokenType.STRING, "\"" + key + "\"")

    def handle_number(self):
        key = ""
        while self.is_digit(self.source[self.i]):
            key += self.source[self.i]
            self.i += 1

        self.make_token(TokenType.NUMBER, key)

    def consume(self):
        self.consume_whitespace()

        char = self.source[self.i]
        match char:
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
                raise Exception(f"Unexpected character: {char}")

    def lex(self) -> List[Token]:
        if len(self.source) == 0:
            return

        if self.source[self.i] != "{":
            raise Exception("json must begin with \"{\"")
        self.i += 1

        while self.source[self.i] != "}":
            if self.i >= len(self.source):
                raise Exception("json must end with \"}\"")

            self.consume()

        return self.tokens


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.i = 0
        self.result: Dict[str, str | int] = {}

    def handle_key_value(self):
        key_token = self.tokens[self.i]
        key = key_token.lexeme[1:-1]     # remove the quotes

        self.i += 1     # consume the string token itself

        if self.i >= len(self.tokens):
            raise Exception("Invalid syntax")

        if self.tokens[self.i].tok_type != TokenType.COLON:
            raise Exception("Syntax error; need a colon after a key")

        self.i += 1     # consume the colon

        if self.i >= len(self.tokens):
            raise Exception("Invalid syntax")

        value_token = self.tokens[self.i]
        match value_token.tok_type:
            case TokenType.STRING:
                value = value_token.lexeme[1:-1]
                self.result[key] = value
            case TokenType.NUMBER:
                value = float(value_token.lexeme)
                self.result[key] = value
            case _:
                raise Exception(f"Invalid value for the key \"{key}\"")

        self.i += 1     # consume the value token

        if self.i >= len(self.tokens) - 1:
            return

        if self.tokens[self.i].tok_type != TokenType.COMMA:
            raise Exception(
                "Syntax error; need a comma after a value unless at the end")

        self.i += 1

    def consume(self):
        token = self.tokens[self.i]

        match token.tok_type:
            case TokenType.STRING:
                self.handle_key_value()
            case _:
                raise Exception(f"Unexpected character: {self.tokens[self.i]}")
            # No need to handle NUMBER as it can never be a key

    def parse(self) -> Dict[str, str | int]:
        while self.i < len(self.tokens):
            self.consume()

        return self.result


def main():
    try:
        json = input()

        lexer = Lexer(json)
        tokens = lexer.lex()

        parser = Parser(tokens)
        result = parser.parse()

        pprint(result)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
