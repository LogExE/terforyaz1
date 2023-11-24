
from lexeme import Lexeme, LexemeType


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
        return True

    def __process_rel(self) -> bool:
        if not self.__process_operand():
            return False
        lrel = self.__peek()
        if lrel is not None and lrel.l_type == LexemeType.REL:
            self.__pop()
            if not self.__process_operand():
                return False
        return True

    def __process_operand(self) -> bool:
        le = self.__peek()
        if le is None or le.l_type not in (LexemeType.VAR, LexemeType.CONST):
            self.__set_err("Ожидалася операнд")
            return False
        self.__pop()
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
        return True

    def __process_operator(self) -> bool:
        le1 = self.__peek()
        if le1 is None or le1.l_type not in (LexemeType.VAR, LexemeType.OUTPUT):
            self.__set_err("Ожидалось начало оператора")
            return False
        self.__pop()
        if le1.l_type == LexemeType.VAR:
            le2 = self.__peek()
            if le2 is None or le2.l_type != LexemeType.ASSIGN:
                self.__set_err("Ожидался знак присваивания")
                return False
            self.__pop()
            if not self.__process_arithexpr():
                return False
        else:
            if not self.__process_operand():
                return False
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
        las = self.__peek()
        if las is None or las.l_type != LexemeType.ASSIGN:
            self.__set_err("Ожидался знак присваивания")
            return False
        self.__pop()
        if not self.__process_arithexpr():
            return False
        lto = self.__peek()
        if lto is None or lto.l_type != LexemeType.TO:
            self.__set_err("Ожидался to")
            return False
        self.__pop()
        if not self.__process_arithexpr():
            return False
        if not self.__process_operators():
            return False
        lnext = self.__peek()
        if lnext is None or lnext.l_type != LexemeType.NEXT:
            self.__set_err("Ожидался next")
            return False
        self.__pop()
        return True

    def process(self, lexemes: list[Lexeme]) -> bool:
        self.__idx = 0
        self.__lex = lexemes
        self.__res = self.__process_for()

        return self.__res

    def whatswrong(self) -> tuple[int, str]:
        return (self.__errpos, self.__err)


if __name__ == "__main__":
    from lexer import LexicalAnalyzer
    from pprint import pprint
    print("Введите цепочку для синтаксического анализа. Перед этим на ней будет проведен лекисческий анализ.")
    code = input()
    la = LexicalAnalyzer()
    lexemes = la.process(code)
    print("Результат лексического анализа")
    pprint(lexemes)

    sa = SyntaxAnalyzer()
    syn = sa.process(lexemes)
    print("Результат синтаксического анализа")
    pprint(syn)
    if not syn:
        pos, err = sa.whatswrong()
        print(f"Ошибка около позиции {pos}: {err}")
