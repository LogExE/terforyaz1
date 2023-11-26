
from dataclasses import dataclass
from poliz import PostfixEntry, PostfixEntryType, Command

@dataclass
class LogEntry:
    stack: list[int | str]
    var: dict[str, int]
    cmd_idx: int
    action: str

class Interpreter:
    def __pop_val(self) -> int:
        op = self.__stak.pop()
        if isinstance(op, str):
            if op not in self.__vars:
                self.__vars[op] = int(input("Введите значение переменной " + op + ": "))
            return self.__vars[op]
        return op

    def __push_val(self, val: int) -> None:
        self.__stak.append(val)

    def __push_elem(self, elem: PostfixEntry) -> None:
        self.__stak.append(elem.value)

    def __set_and_pop_var(self, val: int) -> None:
        var = self.__stak.pop()
        self.__vars[var] = val

    cmdbinop = {
        Command.ADD: lambda x, y: x + y,
        Command.SUB: lambda x, y: x - y,
        Command.MUL: lambda x, y: x * y,
        Command.DIV: lambda x, y: x // y,
        Command.CMPE: lambda x, y: x == y,
        Command.CMPNE: lambda x, y: x != y,
        Command.CMPG: lambda x, y: x > y,
        Command.CMPL: lambda x, y: x < y,
        Command.AND: lambda x, y: bool(x and y),
        Command.OR: lambda x, y: bool(x or y)
    }

    def interpret(self, postfix: list[PostfixEntry]) -> None:
        self.__vars = {}
        self.__stak = []
        self.__outs = []
        self.__log = []

        self.__cmd_idx = 0
        while self.__cmd_idx != len(postfix):
            entry = postfix[self.__cmd_idx]
            if entry.type == PostfixEntryType.CMD:
                action = entry.value
                if entry.value == Command.JMP:
                    self.__cmd_idx = self.__pop_val()
                elif entry.value == Command.JZ:
                    tmp = self.__pop_val()
                    if self.__pop_val():
                        self.__cmd_idx += 1
                    else:
                        self.__cmd_idx = tmp
                elif entry.value == Command.SET:
                    self.__set_and_pop_var(self.__pop_val())
                    self.__cmd_idx += 1
                elif entry.value in self.cmdbinop:
                    op1 = self.__pop_val()
                    op2 = self.__pop_val()
                    self.__push_val(self.cmdbinop[entry.value](op2, op1))
                    self.__cmd_idx += 1
                elif entry.value == Command.NOT:
                    self.__push_val(not self.__pop_val())
                    self.__cmd_idx += 1
                elif entry.value == Command.OUT:
                    self.__outs.append(self.__pop_val())
                    self.__cmd_idx += 1
                elif entry.value == Command.NOOP:
                    self.__cmd_idx += 1
            else:
                action = "PUSH"
                self.__push_elem(entry)
                self.__cmd_idx += 1
            self.__log.append(LogEntry(self.__vars.copy(), self.__stak.copy(), self.__cmd_idx, action))

    def logs(self) -> list[LogEntry]:
        return self.__log

    def outputs(self) -> list[int]:
        return self.__outs


if __name__ == "__main__":
    from lexer import LexicalAnalyzer
    from syntaxer import SyntaxAnalyzer
    from tabulate import tabulate
    print("Введите цепочку для интерпретации.")
    code = input()
    la = LexicalAnalyzer()
    lexemes = la.process(code)

    sa = SyntaxAnalyzer()
    syn = sa.process(lexemes)
    if not syn:
        pos, err = sa.whatswrong()
        print(f"Ошибка около позиции {pos}: {err}")
    else:
        ipr = Interpreter()
        ipr.interpret(sa.poliz())
        print(tabulate([(i, ent.cmd_idx, ent.stack, ent.var, ent.action) for i, ent in enumerate(ipr.logs())], 
                       headers=["Шаг", "Счетчик команд", "Стек", "Переменные", "Действие"]))
        print("Выводы:")
        print(ipr.outputs())
