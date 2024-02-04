from abc import ABC, abstractmethod
from enum import Enum


# This is also the precedence of tokens.
class TokenKind(Enum):
    PLUS = 0
    MULTIPLY = 1
    NUMBER = 2

    def increase(self) -> "TokenKind":
        value = self.value + 1
        if value >= self.__class__.NUMBER.value:
            return self.__class__.NUMBER
        return getattr(self.__class__, self.__class__._member_names_[value])


class Token(object):
    def __init__(self, lexeme: str, kind: TokenKind) -> None:
        self.lexeme = lexeme
        self.kind = kind


# A toy scan function.
def simple_scan(source: str) -> list[Token]:
    tokens = []
    for char in source:
        if char.isspace():
            continue
        if char.isdigit():
            tokens.append(Token(char, TokenKind.NUMBER))
        elif char == "+":
            tokens.append(Token(char, TokenKind.PLUS))
        elif char == "*":
            tokens.append(Token(char, TokenKind.MULTIPLY))
        else:
            raise ValueError(f"Unresolved token {char}")
    return tokens


class BytecodeInstruction(ABC):
    @abstractmethod
    def __str__(self) -> str: ...


class ConstantInstruction(BytecodeInstruction):
    def __init__(self, value: int) -> None:
        self.value = value

    def __str__(self) -> str:
        return f"CONST {self.value}"


class AddInstruction(BytecodeInstruction):
    def __str__(self) -> str:
        return "ADD"


class MultiplyInstruction(BytecodeInstruction):
    def __str__(self) -> str:
        return "MUL"


class PrattParser(object):
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0
        self.jumptable = {
            TokenKind.NUMBER: (self.number, None),
            TokenKind.PLUS: (None, self.binary),
            TokenKind.MULTIPLY: (None, self.binary),
        }
        self.bytecode = []

    def emit(self, instruction: BytecodeInstruction) -> None:
        self.bytecode.append(instruction)
        print(instruction)

    def parse_precedence(self, precedence: int) -> None:
        if self.current >= len(self.tokens):
            return None
        start = self.tokens[self.current]
        # Retrieve the next jump when the token is as prefix.
        # We can use match cases here in order to get rid of function pointer table.
        jump = self.jumptable[start.kind][0]
        jump()
        while (
            self.current < len(self.tokens)
            and precedence <= self.tokens[self.current].kind.value
        ):
            # Retrieve the next jump when the token is as infix.
            # We can use match here again.
            jump = self.jumptable[self.tokens[self.current].kind][1]
            jump()

    def number(self) -> None:
        if self.current >= len(self.tokens):
            return None
        self.current += 1
        self.emit(ConstantInstruction(int(self.tokens[self.current - 1].lexeme)))

    def binary(self) -> None:
        if self.current >= len(self.tokens):
            return None
        operator = self.tokens[self.current]
        self.current += 1
        self.parse_precedence(operator.kind.increase().value)
        match operator.kind:
            case TokenKind.MULTIPLY:
                self.emit(MultiplyInstruction())
            case TokenKind.PLUS:
                self.emit(AddInstruction())


def interpret(bytecode: list[BytecodeInstruction]) -> None:
    stack = []

    def print_stack():
        nonlocal stack
        for element in stack:
            print(f"[ {element} ]", end="")
        print()

    for instruction in bytecode:
        if isinstance(instruction, ConstantInstruction):
            stack.append(instruction.value)
        elif isinstance(instruction, MultiplyInstruction):
            b = stack.pop()
            a = stack.pop()
            stack.append(a * b)
        elif isinstance(instruction, AddInstruction):
            b = stack.pop()
            a = stack.pop()
            stack.append(a + b)
        else:
            raise NotImplementedError()
        print(instruction, end="\t")
        print_stack()


def main():
    source = "1 + 2 * 3 + 4"
    tokens = simple_scan(source)
    parser = PrattParser(tokens)
    print("=== BYTECODE ===")
    parser.parse_precedence(0)
    print("=== Interpret ===")
    interpret(parser.bytecode)


# Guideline recommended Main Guard
if __name__ == "__main__":
    main()
