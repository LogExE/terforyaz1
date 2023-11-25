
from lexeme import Lexeme, LexemeType
from poliz import PostfixEntryType, PostfixEntry, Command


class SyntaxAnalyzer:
    def __peek(self) -> Lexeme | None:
        try:
            return self.__lex[self.__idx]
        except IndexError:
            return None

    def __pop(self) -> Lexeme | None:
        peek = self.__peek()
        if peek is not None:
            self.__idx += 1
        return peek

    def __set_err(self, err: str) -> None:
        self.__errpos = self.__idx
        self.__err = err

    def __add_cmd(self, cmd: Command) -> int:
        self.__poliz.append(PostfixEntry(PostfixEntryType.CMD, cmd))
        return self.__poliz_cur_addr()

    def __add_var(self, name: str) -> int:
        self.__poliz.append(PostfixEntry(PostfixEntryType.VAR, name))
        return self.__poliz_cur_addr()

    def __add_const(self, val: str) -> int:
        self.__poliz.append(PostfixEntry(PostfixEntryType.CONST, int(val)))
        return self.__poliz_cur_addr()

    def __add_addr(self, addr: int) -> int:
        self.__poliz.append(PostfixEntry(PostfixEntryType.CMD_PTR, addr))
        return self.__poliz_cur_addr()

    def __poliz_cur_addr(self) -> int:
        return len(self.__poliz) - 1
    
    def __set_addr(self, idx: int, addr: int) -> None:
        self.__poliz[idx].value = addr

    relcmd = {
        "==": Command.CMPE,
        "<>": Command.CMPNE,
        ">": Command.CMPG,
        "<": Command.CMPL
    }

    aopmcmd = {
        "+": Command.ADD,
        "-": Command.SUB
    }

    aomdcmd = {
        "*": Command.MUL,
        "/": Command.DIV
    }

    def __process_condition(self) -> bool:
        if not self.__process_condition1():
            return False
        while True:
            lor = self.__peek()
            if lor is None or lor.l_type != LexemeType.OR:
                break
            self.__pop()
            if not self.__process_condition1():
                return False
            self.__add_cmd(Command.OR)
        return True

    def __process_condition1(self) -> bool:
        if not self.__process_condition2():
            return False
        while True:
            land = self.__peek()
            if land is None or land.l_type != LexemeType.AND:
                break
            self.__pop()
            if not self.__process_condition2():
                return False
            self.__add_cmd(Command.AND)
        return True

    def __process_condition2(self) -> bool:
        le1 = self.__peek()
        if le1 is None:
            self.__set_err("Ожидалось условие")
            return False
        if le1.l_type == LexemeType.NOT:
            self.__pop()
        if not self.__process_rel():
            return False
        if le1.l_type == LexemeType.NOT:
            self.__add_cmd(Command.NOT)
        return True

    def __process_rel(self) -> bool:
        if not self.__process_operand():
            return False
        lrel = self.__peek()
        if lrel is not None and lrel.l_type == LexemeType.REL:
            self.__pop()
            if not self.__process_operand():
                return False
            self.__add_cmd(self.relcmd[lrel.val])
        return True

    def __process_operand(self) -> bool:
        le = self.__peek()
        if le is None or le.l_type not in (LexemeType.VAR, LexemeType.CONST):
            self.__set_err("Ожидалася операнд")
            return False
        self.__pop()
        if le.l_type == LexemeType.VAR: # poliz var operand
            self.__add_var(le.val) 
        else: # poliz const operand
            self.__add_const(le.val)  
        return True

    def __process_arithexpr(self) -> bool:
        if not self.__process_arithexpr1():
            return False
        while True:
            laopm = self.__peek()
            if laopm is None or laopm.l_type != LexemeType.AOPM:
                break
            self.__pop()
            if not self.__process_arithexpr1():
                return False
            self.__add_cmd(self.aopmcmd[laopm.val]) # poliz add | sub
        return True

    def __process_arithexpr1(self) -> bool:
        if not self.__process_operand():
            return False
        while True:
            laomd = self.__peek()
            if laomd is None or laomd.l_type != LexemeType.AOMD:
                break
            self.__pop()
            if not self.__process_operand():
                return False
            self.__add_cmd(self.aomdcmd[laomd.val]) # poliz mul | div
        return True

    def __process_operator(self) -> bool:
        le1 = self.__peek()
        if le1 is None or le1.l_type not in (LexemeType.VAR, LexemeType.OUTPUT):
            self.__set_err("Ожидалось начало оператора")
            return False
        self.__pop()
        if le1.l_type == LexemeType.VAR:
            self.__add_var(le1.val) # poliz assignment var
            le2 = self.__peek()
            if le2 is None or le2.l_type != LexemeType.ASSIGN:
                self.__set_err("Ожидался знак присваивания")
                return False
            self.__pop()
            if not self.__process_arithexpr():
                return False
            self.__add_cmd(Command.SET) # poliz assignment cmd
        else:
            if not self.__process_operand():
                return False
            self.__add_cmd(Command.OUT)
        return True

    def __process_operators(self) -> bool:
        if not self.__process_operator():
            return False
        while True:
            semicol = self.__peek()
            if semicol is None or semicol.l_type != LexemeType.SEMICOL:
                break
            self.__pop()
            if not self.__process_operator():
                return False
        return True

    def __process_for(self) -> bool:
        ind_first = len(self.__poliz) # poliz begin addr
        lfor = self.__peek()
        if lfor is None or lfor.l_type != LexemeType.FOR:
            self.__set_err("Ожидался for")
            return False
        self.__pop()
        lvar = self.__peek()
        if lvar is None or lvar.l_type != LexemeType.VAR:
            self.__set_err("Ожидалась перменная цикла")
            return False
        self.__pop()
        self.__add_var(lvar.val) # poliz for variable
        las = self.__peek()
        if las is None or las.l_type != LexemeType.ASSIGN:
            self.__set_err("Ожидался знак присваивания")
            return False
        self.__pop()
        if not self.__process_arithexpr():
            return False
        self.__add_cmd(Command.SET) # poliz for var set
        lto = self.__peek()
        if lto is None or lto.l_type != LexemeType.TO:
            self.__set_err("Ожидался to")
            return False
        self.__pop()
        self.__add_var(lvar.val) # poliz for condition 
        if not self.__process_arithexpr():
            return False
        self.__add_cmd(Command.CMPG)
        self.__add_cmd(Command.NOT) # poliz check for condition
        ind_jmp = self.__add_addr(-1) # dummy value
        self.__add_cmd(Command.JZ)
        if not self.__process_operators():
            return False
        self.__add_var(lvar.val) 
        self.__add_const(1)
        self.__add_cmd(Command.ADD) # poliz for var increment
        lnext = self.__peek()
        if lnext is None or lnext.l_type != LexemeType.NEXT:
            self.__set_err("Ожидался next")
            return False
        self.__pop()
        self.__add_addr(ind_first)
        ind_last = self.__add_cmd(Command.JMP)
        self.__set_addr(ind_jmp, ind_last + 1)
        return True

    def process(self, lexemes: list[Lexeme]) -> bool:
        self.__idx = 0
        self.__lex = lexemes
        self.__poliz: list[PostfixEntry] = []

        self.__res = self.__process_for()
        if self.__res and self.__idx != len(lexemes):
            self.__set_err("Неожиданная лексема в конце")
            self.__res = False
        if self.__res:
            self.__add_cmd(Command.NOOP)

        return self.__res

    def whatswrong(self) -> tuple[int, str]:
        return (self.__errpos, self.__err)
    
    def poliz(self) -> list[PostfixEntry]:
        return self.__poliz


if __name__ == "__main__":
    from lexer import LexicalAnalyzer
    from pprint import pprint
    print("Введите цепочку для синтаксического анализа. Перед этим на ней будет проведен лекисческий анализ.")
    code = input()
    la = LexicalAnalyzer()
    lexemes = la.process(code)
    print("Результат лексического анализа")
    for i, l in enumerate(lexemes):
        print(f"{i}: позиция {l.pos}, тип {l.l_type}, значение {l.val}")

    sa = SyntaxAnalyzer()
    syn = sa.process(lexemes)
    print("Результат синтаксического анализа")
    pprint(syn)
    if not syn:
        pos, err = sa.whatswrong()
        print(f"Ошибка около позиции {pos}: {err}")
    else:
        print("ПОЛИЗ:")
        for i, pe in enumerate(sa.poliz()):
            print(f"{i}: тип {pe.type}, значение {pe.value}")