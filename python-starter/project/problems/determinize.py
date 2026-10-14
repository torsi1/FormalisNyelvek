import argparse
import sys

from project.problem import Problem

class DeterminizeProblem(Problem):

    def __init__(self):
        super().__init__()
        # az objektum letrehozasa
        self.start = "" # kezdoallapot
        self.accepting = set() # vegallapotok
        self.transitions = {} # atmenetek
        self.states = [] # allapotok
        self.alphabet = [] # abc

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--det",
            action="store_true",
            help="Az automata determinalizálása",
        )

    def is_chosen_problem(self, args):
        return args.det

    def load(self, path):
        with open(path, encoding="utf-8") as f:
            lines = [line.strip() for line in f.read().splitlines()]

        self.states = lines[0].split()
        self.alphabet = lines[1].split()
        self.start = lines[2].split()[0]
        self.accepting = set(lines[3].split())

        self.transitions = {}
        for line in lines[4:]:
            parts = line.split()
            if not parts:
                continue
            if len(parts) != 3:
                raise ValueError(f"Hibás átmenet sor: '{line}'")
            src, symbol, dst = parts
            if src not in self.states or dst not in self.states:
                raise ValueError(f"Ismeretlen állapot: '{line}'")
            if symbol not in self.alphabet:
                raise ValueError(f"Ismeretlen szimbólum: '{line}'")
            self.transitions.setdefault((src, symbol), set()).add(dst)

    def determinize(self):
        symbols = sorted(self.alphabet)

        start_set = frozenset([self.start])
        names = {start_set: 0}   # halmaz -> sorszam
        order = [start_set]      # felfedezes sorrendje
        result = []              # (honnan, jel, hova)

        i = 0
        while i < len(order):
            current = order[i]
            for symbol in symbols:
                target = set()
                for q in current:
                    target |= self.transitions.get((q, symbol), set())
                if not target:
                    continue
                target = frozenset(target)
                if target not in names:
                    names[target] = len(order)
                    order.append(target)
                result.append((i, symbol, names[target]))
            i += 1

        final = [f"s{n}" for n, subset in enumerate(order)
                if subset & self.accepting]
        return len(order), final, result

    def run(self, args):
        try:
            self.load(args.input)
        except (ValueError, IndexError) as e:
            print(f"Hiba a bemenet beolvasásakor: {e}", file=sys.stderr)
            sys.exit(1)

        count, final, result = self.determinize()

        out = [
            " ".join(f"s{n}" for n in range(count)),
            " ".join(self.alphabet),
            "s0",
            " ".join(final),
        ]
        for src, symbol, dst in result:
            out.append(f"s{src} {symbol} s{dst}")

        with open(args.output, "w", encoding="utf-8") as f:
            f.write("\n".join(out) + "\n")