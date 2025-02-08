from typing import Dict, List
from enum import Enum, auto
from pprint import pprint


class TokenType(Enum):
    LSQUIRLY = auto()
    RSQUIRLY = auto()
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
            raise Exception("Unterminated string")

        self.i += 1     # consume the last "
        self.make_token(TokenType.STRING, "\"" + key + "\"")

    def handle_number(self):
        key = ""
        while self.is_digit(self.source[self.i]):
            if self.is_at_end():
                raise Exception("json input ended abrupty")

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
                raise Exception(f"Unexpected character: {char}")

    def lex(self) -> List[Token]:
        while self.i < len(self.source):
            self.consume()

        return self.tokens


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.i = 0
        self.result: Dict[str, str | float] = {}

    def consume(self, expected: str):
        if self.is_at_end():
            raise Exception("json input ended abruptly")

        found = self.curr().lexeme
        if found != expected:
            raise Exception(f"Expected {expected} but got {found}")

        self.i += 1

    def match(self, expected: str) -> bool:
        if self.is_at_end():
            raise Exception("json input ended abruptly")

        found = self.curr().lexeme
        if found != expected:
            return False

        self.i += 1
        return True

    def is_at_end(self) -> bool:
        return self.i >= len(self.tokens)

    def curr(self) -> Token:
        if self.is_at_end():
            return None

        return self.tokens[self.i]

    def next(self) -> Token | None:
        if self.i >= len(self.tokens) - 1:
            return None

        return self.tokens[self.i + 1]

    def key(self) -> str:
        curr = self.curr()
        if curr is None or curr.tok_type != TokenType.STRING:
            raise Exception("Expected string")

        key = curr.lexeme[1:-1]
        self.i += 1
        return key

    def value(self):
        value = 0
        curr = self.curr()

        if curr is None:
            raise Exception("Expected a value for the corresponding key")

        match curr.tok_type:
            case TokenType.STRING:
                value = curr.lexeme[1:-1]
            case TokenType.NUMBER:
                value = float(curr.lexeme)
            case _:
                raise Exception("Expected string or number")

        self.i += 1
        return value

    def pair(self):
        key = self.key()
        self.consume(":")
        value = self.value()

        self.result[key] = value

    def json(self):
        self.consume("{")

        while True:
            if self.match("}"):
                break

            self.pair()

            if self.match("}"):
                break

            self.consume(",")

    def parse(self) -> Dict[str, str | float]:
        self.json()

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
