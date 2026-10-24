import argparse
from project.problem import Problem

class MinimalizeProblem(Problem):

    def __init__(self):
        super().__init__()
        # Az objektum létrehozása
        self.states = []
        self.alphabet = []
        self.start = ""  # Kezdőállapot
        self.accepting = set()  # Végállapotok
        self.transitions = {}  # Átmenetek

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--mini",
            action="store_true",
            help="Jelezzük a programnak, hogy minimalizálni kell az adott automatát.",
        )

    def is_chosen_problem(self, args):
        return args.mini

    def load(self, path):
        with open(path, encoding="utf-8") as f:
            lines = [line.strip() for line in f.read().splitlines() if line.strip()]

        if len(lines) < 4:
            raise ValueError("Hiba: A bemeneti fájl nem tartalmaz elegendő sort.")

        self.states = lines[0].split()
        self.alphabet = lines[1].split()
        self.start = lines[2].split()[0]
        self.accepting = set(lines[3].split())

        # Alapvető hibakezelés: ellenőrzés, hogy a kezdőállapot és a végállapotok léteznek-e
        if self.start not in self.states:
            raise ValueError(f"Hiba: A kezdőállapot ({self.start}) nincs az állapotok között.")
        for acc in self.accepting:
            if acc not in self.states:
                raise ValueError(f"Hiba: A végállapot ({acc}) nincs az állapotok között.")

        self.transitions = {}
        for line in lines[4:]:
            parts = line.split()
            if len(parts) != 3:
                continue
            src, symbol, dst = parts
            if src not in self.states or dst not in self.states or symbol not in self.alphabet:
                raise ValueError(f"Hiba: Érvénytelen átmenet vagy szimbólum: {src} {symbol} {dst}")
            self.transitions[(src, symbol)] = dst

    def run(self, args):
        self.load(args.input)

        # DFA minimalizálás particionálásfinomítással (Moore-algoritmus)
        states = self.states
        alphabet = self.alphabet

        F = self.accepting & set(states)    # végállapotok halmaza
        not_F = set(states) - F         # nem végállapotok halmaza
        P = []
        if F:
            P.append(F)
        if not_F:
            P.append(not_F)

        while True:
            new_P = []
            for group in P:
                splits = {}
                for state in group:
                    signature = tuple(      # állapot aláírása: a szimbólumokhoz tartozó célállapotok indexei a P-ben
                        next((i for i, b in enumerate(P) if self.transitions.get((state, sym)) in b), -1)
                        for sym in alphabet
                    )       # b - csoport, amelybe az átmenet célállapota tartozik
                    if signature not in splits:
                        splits[signature] = set()       # ha még nincs ilyen aláírás, létrehozunk egy új csoportot
                    splits[signature].add(state)        # hozzáadjuk az állapotot a megfelelő csoporthoz
                new_P.extend(splits.values())           # új csoportok hozzáadása a listához
            if len(new_P) == len(P):                    # ha nincs változás, akkor elértük a stabil állapotot
                break
            P = new_P

        # Állapotok átnevezése az összevont csoportok legkisebb neve alapján ('s' prefixummal)
        block_map = {}
        new_states_set = set()

        for group in P:         # minden csoporthoz hozzárendeljük a legkisebb állapot nevét
            min_state = min(
                group,
                key=lambda s: int(''.join(filter(str.isdigit, s))) if any(c.isdigit() for c in s) else s
            )
            if min_state.startswith('q'):       # átnevezés: 'q' prefixumot 's'-re cseréljük, a számot megtartva
                new_name = 's' + min_state[1:]
            else:
                new_name = 's' + ''.join(filter(str.isdigit, min_state)) if any(c.isdigit() for c in min_state) else 's_' + min_state

            new_states_set.add(new_name)
            for state in group:
                block_map[state] = new_name

        # Új állapotok rendezése index szerint
        new_states = sorted(
            list(new_states_set),
            key=lambda s: int(''.join(filter(str.isdigit, s))) if any(c.isdigit() for c in s) else s
        )

        new_start = block_map[self.start]       # új kezdőállapot meghatározása a blokk térképből
        new_accepting = sorted(list({block_map[acc] for acc in self.accepting if acc in block_map}))       # új végállapotok meghatározása a blokk térképből, rendezve

        # Új átmenetek generálása
        new_transitions = set()
        for group in P:     # minden csoporthoz hozzárendeljük a legkisebb állapot nevét, és az átmeneteket az új állapotokra irányítjuk
            rep = min(
                group,
                key=lambda s: int(''.join(filter(str.isdigit, s))) if any(c.isdigit() for c in s) else s
            )
            src_new = block_map[rep]        # az új állapot neve a blokk térképből
            for sym in alphabet:        # minden szimbólumhoz megnézzük, hogy van-e átmenet a reprezentatív állapotból
                if (rep, sym) in self.transitions:
                    dst_old = self.transitions[(rep, sym)]      # a régi célállapot
                    dst_new = block_map[dst_old]                # az új célállapot a blokk térképből
                    new_transitions.add((src_new, sym, dst_new))        # az új átmenet hozzáadása a halmazhoz

        # Átmenetek rendezése: kiindulási állapot, szimbólum, majd célállapot szerint
        sorted_transitions = sorted(
            list(new_transitions),
            key=lambda t: (
                int(''.join(filter(str.isdigit, t[0]))) if any(c.isdigit() for c in t[0]) else t[0],
                t[1],
                int(''.join(filter(str.isdigit, t[2]))) if any(c.isdigit() for c in t[2]) else t[2]
            )
        )

        # Kimenet összeállítása
        output_lines = [        # új állapotok, ábécé, kezdőállapot, végállapotok
            " ".join(new_states),
            " ".join(alphabet),
            new_start,
            " ".join(new_accepting)
        ]
        for src, sym, dst in sorted_transitions:    # rendezett átmenetek hozzáadása a kimenethez
            output_lines.append(f"{src} {sym} {dst}")

        with open(args.output, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines) + "\n")