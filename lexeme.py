from enum import Enum
from dataclasses import dataclass


class LexemeType(Enum):
    FOR = 0
    TO = 1
    NEXT = 2
    AND = 3
    OR = 4
    NOT = 5
    OUTPUT = 6
    AOPM = 7
    AOMD = 8
    REL = 9
    SEMICOL = 10
    ASSIGN = 11
    VAR = 12
    CONST = 13


@dataclass
class Lexeme:
    l_type: LexemeType
    pos: int
    val: str
