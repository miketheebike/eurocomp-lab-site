"""
Fixes raw HTML blocks whose inner lines are indented 4+ spaces.

Markdown reads a 4-space indent as a code block, so the HTML renders as
literal text instead of as markup. Reducing the indent to 2 spaces keeps
the file readable and lets the HTML render.

Preview:  python3 fix-indent.py
Apply:    python3 fix-indent.py --fix
"""
import glob, re, sys

apply_fix = "--fix" in sys.argv
OPEN  = re.compile(r'^\s*<div class="further-reading"')
CLOSE = re.compile(r'^\s*</div>\s*$')

touched = []
for path in sorted(glob.glob("*.qmd")):
    lines = open(path, encoding="utf-8").read().split("\n")
    inside, depth, hits = False, 0, []

    for i, line in enumerate(lines):
        if OPEN.match(line):
            inside, depth = True, 0
        if not inside:
            continue

        depth += line.count("<div") - line.count("</div>")

        lead = len(line) - len(line.lstrip(" "))
        if lead >= 4 and line.strip():
            hits.append(i + 1)
            if apply_fix:
                lines[i] = "  " + line.lstrip(" ")

        if depth <= 0 and CLOSE.match(line):
            inside = False

    if hits:
        touched.append((path, hits))
        if apply_fix:
            open(path, "w", encoding="utf-8").write("\n".join(lines))

if not touched:
    print("No over-indented HTML found.")
else:
    verb = "fixed" if apply_fix else "would fix"
    total = sum(len(h) for _, h in touched)
    print(f"{verb} {total} lines across {len(touched)} files"
          + ("" if apply_fix else "   (run with --fix to apply)") + "\n")
    for p, h in touched:
        shown = ", ".join(str(n) for n in h[:10])
        more = f" ... +{len(h)-10} more" if len(h) > 10 else ""
        print(f"  {p}  lines {shown}{more}")
