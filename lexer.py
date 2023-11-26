from enum import Enum
from lexeme import Lexeme, LexemeType


class LexicalAnalyzer:
    class State(Enum):
        S = 0  # start
        Ai = 1
        Ac = 2
        As = 3
        Bs = 4
        Cs = 5
        Ds = 6
        Gs = 7
        E = 8  # if error
        F = 9  # final

    def __add_lex(self, state: State, code: str, start: int, end: int) -> None:
        lt = None
        val = code[start:end]
        if state == self.State.Ai:
            if val == "for":
                lt = LexemeType.FOR
            elif val == "to":
                lt = LexemeType.TO
            elif val == "next":
                lt = LexemeType.NEXT
            elif val == "output":
                lt = LexemeType.OUTPUT
            elif val == "or":
                lt = LexemeType.OR
            elif val == "and":
                lt = LexemeType.AND
            elif val == "not":
                lt = LexemeType.NOT
            else:
                lt = LexemeType.VAR
        elif state == self.State.Ac:
            lt = LexemeType.CONST
        elif state in (self.State.As, self.State.Ds, self.State.Bs, self.State.Gs, self.State.Cs):
            if val in (">", "==", "<", "<>"):
                lt = LexemeType.REL
            elif val in ("+", "-"):
                lt = LexemeType.AOPM
            elif val in ("*", "/"):
                lt = LexemeType.AOMD
            elif val == ";":
                lt = LexemeType.SEMICOL
            elif val == "=":
                lt = LexemeType.ASSIGN
        lex = Lexeme(lt, start, val)
        self.__res.append(lex)

    def process(self, code: str) -> list[Lexeme]:
        self.__state = self.State.S
        self.__res: list[Lexeme] = []

        idx = 0
        while self.__state not in (self.State.E, self.State.F):
            prev_state = self.__state
            need_to_add = True

            c = code[idx] if idx < len(code) else "\0"

            if self.__state == self.State.S:
                if c.isspace():
                    pass
                elif c.isalpha():
                    self.__state = self.State.Ai
                elif c.isdigit():
                    self.__state = self.State.Ac
                elif c == "<":
                    self.__state = self.State.As
                elif c == "=":
                    self.__state = self.State.Bs
                elif c in "+-/*;>":
                    self.__state = self.State.Cs
                elif c == "\0":
                    self.__state = self.State.F
                else:
                    self.__state = self.State.E
                need_to_add = False
            elif self.__state == self.State.Ai:
                if c.isspace():
                    self.__state = self.State.S
                elif c.isalnum():
                    need_to_add = False
                elif c == "<":
                    self.__state = self.State.As
                elif c == "=":
                    self.__state = self.State.Bs
                elif c in "+-/*;>":
                    self.__state = self.State.Cs
                elif c == "\0":
                    self.__state = self.State.F
                else:
                    self.__state = self.State.E
                    need_to_add = False
            elif self.__state == self.State.Ac:
                if c.isspace():
                    self.__state = self.State.S
                elif c.isdigit():
                    need_to_add = False
                elif c == "<":
                    self.__state = self.State.As
                elif c == "=":
                    self.__state = self.State.Bs
                elif c in "+-/*;>":
                    self.__state = self.State.Cs
                elif c == "\0":
                    self.__state = self.State.F
                else:
                    self.__state = self.State.E
                    need_to_add = False
            elif self.__state == self.State.As:
                if c.isspace():
                    self.__state = self.State.S
                elif c.isalpha():
                    self.__state = self.State.Ai
                elif c.isdigit():
                    self.__state = self.State.Ac
                elif c == ">":
                    self.__state = self.State.Ds
                    need_to_add = False
                elif c == "\0":
                    self.__state = self.State.F
                else:
                    self.__state = self.State.E
                    need_to_add = False
            elif self.__state == self.State.Bs:
                if c.isspace():
                    self.__state = self.State.S
                elif c.isalpha():
                    self.__state = self.State.Ai
                elif c.isdigit():
                    self.__state = self.State.Ac
                elif c == "=":
                    self.__state = self.State.Gs
                    need_to_add = False
                elif c == "\0":
                    self.__state = self.State.F
                else:
                    self.__state = self.State.E
                    need_to_add = False
            elif self.__state in (self.State.Cs, self.State.Ds, self.State.Gs):
                if c.isspace():
                    self.__state = self.State.S
                elif c.isalpha():
                    self.__state = self.State.Ai
                elif c.isdigit():
                    self.__state = self.State.Ac
                elif c == "\0":
                    self.__state = self.State.F
                else:
                    self.__state = self.State.E
                    need_to_add = False
            if need_to_add:
                self.__add_lex(prev_state, code, lex_start, idx)
            if self.__state != prev_state and self.__state in (self.State.Ai, self.State.Ac, self.State.As, self.State.Bs, self.State.Cs):
                lex_start = idx
            if self.__state not in (self.State.E, self.State.F):
                idx += 1
            i = 0
            while i < len(self.__res) - 2:
                x, y, z = self.__res[i:i+3]
                if x.l_type not in (LexemeType.VAR, LexemeType.CONST) and y.l_type == LexemeType.AOPM and z.l_type == LexemeType.CONST:
                    self.__res[i + 1] = Lexeme(LexemeType.CONST,
                                               y.pos, y.val + z.val)
                    self.__res.pop(i + 2)
                i += 1
        return self.__res


if __name__ == "__main__":
    la = LexicalAnalyzer()
    print("Введите цепочку для лексического анализа:")
    code = input()
    res = la.process(code)
    print("Результат")
    for i, l in enumerate(res):
        print(f"{i}: позиция {l.pos}, тип {l.l_type}, значение {l.val}")
