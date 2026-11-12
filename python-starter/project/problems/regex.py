import argparse
import re
from collections import Counter
from project.problem import Problem


class RegexProblem(Problem):

    def __init__(self):
        super().__init__()
        # Az objektum létrejötte és adattagjai
        self.lines = []

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--rgx",
            type=int,
            default=None,
            help="A végrehajtandó regexes feladat sorszáma (1-5)",
        )

    def is_chosen_problem(self, args):
        return args.rgx is not None

    def load(self, path):
        with open(path, "r", encoding="utf-8") as f:
            self.lines = [line.rstrip("\n") for line in f]

    def run(self, args):
        self.load(args.input)

        results = []
        rgx_num = args.rgx

        # Közös alapminta a log sorok biztonságos feldolgozásához
        # Dátum/idő, PID, TID, Log szint (I/D/V/E/F/A/W), Tag, Üzenet
        base_pattern = re.compile(
            r"^([0-9-]+ +[0-9:.]+) +([0-9]+) +([0-9]+) ([IDVEFAW]) (.+?): (?:(.+))?"
        )

        if rgx_num == 1:
            # Alpontok megoldása regexekkel:
            # 1.1: Összes sor, ami 10. hónap 15-én jött létre (10-15)
            p1 = re.compile(r"^10-15")
            count_1 = sum(1 for l in self.lines if p1.search(l))

            # 1.2: 10. hónap 15-én 10 óra 18 perc és 51 másodperckor (10-15 10:18:51)
            p2 = re.compile(r"^10-15 10:18:51")
            count_2 = sum(1 for l in self.lines if p2.search(l))

            # 1.3: Összes sor, ami 51 másodperckor jött létre
            p3 = re.compile(r":\d{2}:51")
            count_3 = sum(1 for l in self.lines if p3.search(l))

            # 1.4: Összes lowmemorykiller taget tartalmazó sor
            p4 = re.compile(r"\blowmemorykiller\b")
            count_4 = sum(1 for l in self.lines if p4.search(l))

            # 1.5: 10:18:51 kor keletkező 221-es process id-jú sor
            p5 = re.compile(r"^10-15 10:18:51\.\d+\s+221\b")
            count_5 = sum(1 for l in self.lines if p5.search(l))

            # 1.6: Összes hibát tartalmazó sor (E)
            p6 = re.compile(r"\s+E\s+")
            count_6 = sum(1 for l in self.lines if p6.search(l))

            # 1.7: Összes warning (W) amit a PackageManager küld
            p7 = re.compile(r"\s+W\s+PackageManager\b")
            count_7 = sum(1 for l in self.lines if p7.search(l))

            # 1.8: Összes ExoPlayer-es debug (D) infó
            p8 = re.compile(r"\s+D\s+.*ExoPlayer")
            count_8 = sum(1 for l in self.lines if p8.search(l))

            # 1.9: Összes java állomány pozíciót tartalmazó hiba és warning (.java:)
            p9 = re.compile(r"\s+[EW]\s+.*\.java:")
            count_9 = sum(1 for l in self.lines if p9.search(l))

            # 1.10: Összes olyan sor, ami tartalmazza a Thread szót a message részben
            p10 = re.compile(
                r"^([0-9-]+ +[0-9:.]+) +([0-9]+) +([0-9]+) ([IDVEFAW]) (.+?): (?:(.+))?"
            )
            count_10 = 0
            for l in self.lines:
                m = p10.match(l)
                if m and m.group(6):
                    message_part = m.group(6)
                    if re.search(r"\bThread\b", message_part):
                        count_10 += 1

            results = [
                str(count_1),
                str(count_2),
                str(count_3),
                str(count_4),
                str(count_5),
                str(count_6),
                str(count_7),
                str(count_8),
                str(count_9),
                str(count_10),
            ]

        elif rgx_num == 2:
            # 2. feladat: Összes hiba (E sorok) származási helye (stack trace fájlneve)
            stack_pattern = re.compile(r"([A-Za-z0-9_]+)\.java:")
            for l in self.lines:
                if " E " in l or l.endswith(" E"):
                    m = stack_pattern.search(l)
                    if m:
                        results.append(m.group(1) + ".java")

        elif rgx_num == 3:
            # 3. feladat: Különböző process id-k megtartása az előfordulási sorrendjükben
            seen_pids = set()
            for l in self.lines:
                m = base_pattern.match(l)
                if m:
                    pid = m.group(2)
                    if pid not in seen_pids:
                        seen_pids.add(pid)
                        results.append(pid)

        elif rgx_num == 4:
            # 4. feladat: A legtöbb errort tartalmazó process
            error_pids = []
            for l in self.lines:
                m = base_pattern.match(l)
                if m and m.group(4) == "E":
                    error_pids.append(m.group(2))

            if error_pids:
                counts = Counter(error_pids)
                max_pid, max_count = counts.most_common(1)[0]
                results.append(f"PID={max_pid} ({max_count} errors)")

        elif rgx_num == 5:
            # 5. feladat: A fő szálon történt hibák (E) száma
            main_thread_errors = 0
            for l in self.lines:
                m = base_pattern.match(l)
                if m:
                    level = m.group(4)
                    pid = m.group(2)
                    tid = m.group(3)
                    if level == "E" and pid == tid:
                        main_thread_errors += 1
            results.append(str(main_thread_errors))

        # Eredmények kiírása a kimeneti fájlba
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("\n".join(results) + ("\n" if results else ""))