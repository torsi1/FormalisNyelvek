import argparse

from project.problem import Problem

class DFAProblem(Problem):

    def __init__(self):
        super().__init__()
        # az objektum letrehozasa
        self.start = "" # kezdoallapot
        self.accepting = set() # vegallapotok
        self.transitions = {} # atmenetek

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--check",
            type=str,
            default=None,
            help="Ellenőrzendő szavak vesszővel elválasztva (idézőjelben) (pl. a,ab,abc)",
        )

    def is_chosen_problem(self, args):
        return args.check is not None

    def load(self, path):
        with open(path, encoding="utf-8") as f:
            lines = [line.strip() for line in f.read().splitlines()]

        # lines[0]: allapotok, lines[1]: abc (az atmenetekbol dolgozunk)
        start = lines[2].split()
        self.start = start[0] if start else ""
        self.accepting = set(lines[3].split())

        self.transitions = {}
        for line in lines[4:]:
            parts = line.split()
            if len(parts) != 3:
                continue
            src, symbol, dst = parts
            self.transitions[(src, symbol)] = dst

    def accepts(self, word):
        # kezdoallapotbol indulva vegigmegyunk a szon, es az atmenetek alapjan lepunk a kovetkezo allapotba
        state = self.start
        for symbol in word:
            key = (state, symbol)
            if key not in self.transitions:
                return False
            state = self.transitions[key]
        return state in self.accepting

    def run(self, args):
        self.load(args.input)

        results = ["IGEN" if self.accepts(word) else "NEM"
                   for word in args.check.split(",")]

        with open(args.output, "w", encoding="utf-8") as f:
            f.write("\n".join(results) + "\n")