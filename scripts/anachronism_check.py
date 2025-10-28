#!/usr/bin/env python3
from pathlib import Path
import re
import sys

BANNED = [
    "internet","computer","smartphone","laptop","email","facebook","twitter","social media",
    "ai","artificial intelligence","machine learning","robot","robotic",
    "airplane","jet","radar","television","tv","radio",
    "antibiotic","penicillin","nuclear","submarine","gps","satellite",
    "smart watch","smartwatch","drone",
]

# lower-case and word-boundary safe regex
BANNED_RE = re.compile(r"\\b(" + "|".join(re.escape(w) for w in BANNED) + r")\\b", flags=re.I)


def check_file(path: Path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    violations = []
    for i, line in enumerate(lines, start=1):
        if BANNED_RE.search(line):
            violations.append((i, line.strip()))
    return violations


def main():
    if len(sys.argv) < 2:
        print("Usage: anachronism_check.py <file1> [file2 ...]")
        sys.exit(2)
    any_bad = False
    for p in sys.argv[1:]:
        path = Path(p)
        if not path.exists():
            print(f"Missing: {p}")
            continue
        v = check_file(path)
        if v:
            any_bad = True
            print(f"=== {p} ===")
            for ln, txt in v:
                print(f"{ln}: {txt}")
            print()
    if not any_bad:
        print("No obvious modern terms found.")
    sys.exit(0 if not any_bad else 1)


if __name__ == '__main__':
    main()
