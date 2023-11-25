
from enum import Enum
from dataclasses import dataclass

class PostfixEntryType(Enum):
    CMD = 0
    VAR = 1
    CONST = 2
    CMD_PTR = 3

class Command(Enum):
    JMP = 0
    JZ = 1
    SET = 2
    ADD = 3
    SUB = 4
    MUL = 5
    DIV = 6
    AND = 7
    OR = 8
    NOT = 9
    CMPE = 10
    CMPNE = 11
    CMPL = 12
    CMPG = 13
    OUT = 14
    NOOP = 15

@dataclass
class PostfixEntry:
    type: PostfixEntryType
    value: object