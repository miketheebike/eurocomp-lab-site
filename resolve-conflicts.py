"""
Resolves merge conflicts in .qmd files, but ONLY where the disagreement is
purely the heading format (### Heading vs **Heading**). Anything else is
left untouched and reported, so real content differences are never dropped.
"""
import glob, re

BLOCK = re.compile(
    r"^<<<<<<<[^\n]*\n(.*?)^=======\n(.*?)^>>>>>>>[^\n]*\n",
    re.S | re.M,
)

def only_formatting(text):
    """True if every non-blank line is a ### heading or a **bold** line."""
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            continue
        if s.startswith("### "):
            continue
        if re.fullmatch(r"\*\*.+\*\*", s):
            continue
        return False
    return True

auto, manual = [], []

for path in sorted(glob.glob("*.qmd")):
    src = open(path, encoding="utf-8").read()
    if "<<<<<<<" not in src:
        continue

    safe = True
    for ours, theirs in BLOCK.findall(src):
        if not (only_formatting(ours) and only_formatting(theirs)):
            safe = False
            break

    if safe:
        resolved = BLOCK.sub(lambda m: m.group(1), src)
        open(path, "w", encoding="utf-8").write(resolved)
        auto.append(path)
    else:
        manual.append(path)

print(f"auto-resolved {len(auto)}, needs review {len(manual)}")
for p in auto:
    print("  resolved:", p)
for p in manual:
    print("  REVIEW BY HAND:", p)
