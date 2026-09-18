"""
Finds the file whose front matter Quarto cannot parse.

Reproduces exactly what Quarto does: take everything between the opening ---
and the next ---, and try to read it as YAML. Reports any file where that
fails, or where the block is never closed.

Searches subfolders too.

    python3 find-yaml-break.py
"""
import glob, sys

try:
    import yaml
except ImportError:
    yaml = None

files = sorted(glob.glob("**/*.qmd", recursive=True))
bad = []

for path in files:
    raw = open(path, encoding="utf-8").read().split("\n")

    if not raw or raw[0].strip() != "---":
        bad.append((path, "no front matter (line 1 is not ---)", raw[:6]))
        continue

    close = next((i for i, l in enumerate(raw[1:], 1) if l.strip() == "---"), None)

    if close is None:
        bad.append((path, "front matter never closed", raw[:8]))
        continue

    block = raw[1:close]

    if any(not l.strip() for l in block):
        bad.append((path, "blank line inside front matter", raw[:close + 3]))
        continue

    if any(l.lstrip().startswith((":::", "**", "#")) for l in block):
        bad.append((path, "page content inside front matter", raw[:close + 3]))
        continue

    if yaml:
        try:
            yaml.safe_load("\n".join(block))
        except Exception as e:
            bad.append((path, f"YAML error: {str(e).splitlines()[0]}", raw[:close + 3]))

print(f"scanned {len(files)} files\n")

if not bad:
    print("Every front matter block parses cleanly.")
    print("If Quarto still fails, the problem is a --- or ---- rule further down a file.")
    sys.exit()

for path, why, head in bad:
    print(f"!! {path}")
    print(f"   {why}")
    for n, line in enumerate(head, 1):
        print(f"   {n:>3} | {line}")
    print()
