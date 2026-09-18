"""
Replaces mid-document horizontal rules written as --- with ***.

Pandoc reads a --- line that follows a blank line as the start of a YAML
metadata block, anywhere in the file, not only at the top. That produces:
    YAMLException: unidentified alias "*The"

*** renders as the same horizontal rule and is never ambiguous.

Preview:  python3 fix-rules.py
Apply:    python3 fix-rules.py --fix
"""
import glob, sys

apply_fix = "--fix" in sys.argv
touched = []

for path in sorted(glob.glob("*.qmd")):
    lines = open(path, encoding="utf-8").read().split("\n")

    # skip past the front matter so its fences are never touched
    start = 0
    if lines and lines[0].strip() == "---":
        close = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), None)
        if close is not None:
            start = close + 1

    hits = []
    for i in range(start, len(lines)):
        if lines[i].strip() != "---":
            continue
        # a --- directly under text is a setext heading, not a rule: leave it
        prev = lines[i - 1].strip() if i > 0 else ""
        if prev:
            continue
        hits.append(i + 1)
        if apply_fix:
            lines[i] = "***"

    if hits:
        touched.append((path, hits))
        if apply_fix:
            open(path, "w", encoding="utf-8").write("\n".join(lines))

if not touched:
    print("No ambiguous --- rules found.")
else:
    verb = "replaced" if apply_fix else "would replace"
    total = sum(len(h) for _, h in touched)
    print(f"{verb} {total} rules across {len(touched)} files"
          + ("" if apply_fix else "  (run with --fix to apply)") + "\n")
    for p, h in touched:
        shown = ", ".join(str(n) for n in h[:8])
        more = f" ... +{len(h)-8} more" if len(h) > 8 else ""
        print(f"  {p}  lines {shown}{more}")
