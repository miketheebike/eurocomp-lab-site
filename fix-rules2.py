"""
Second pass: removes --- dividers that the first pass skipped.

fix-rules.py left alone any --- sitting directly under a non-blank line,
because in Markdown that is a setext heading (Text + --- makes an H2).
But a --- under a ::: fence is not a heading, it is a divider, and Quarto's
file indexer still reads it as the start of a front matter block.

Rules applied here:
  - a --- directly under plain paragraph text  -> left alone (real heading)
  - a --- whose next content is a # heading    -> deleted (heading separates already)
  - any other stray ---                        -> replaced with ***

Preview:  python3 fix-rules2.py
Apply:    python3 fix-rules2.py --fix
"""
import glob, sys

apply_fix = "--fix" in sys.argv
NOT_TEXT = (":::", "#", ">", "|", "```", "***", "---", ":::", "*")
touched = []

for path in sorted(glob.glob("**/*.qmd", recursive=True)):
    lines = open(path, encoding="utf-8").read().split("\n")

    start = 0
    if lines and lines[0].strip() == "---":
        close = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), None)
        if close is not None:
            start = close + 1

    hits, drop = [], set()
    for i in range(start, len(lines)):
        if lines[i].strip() != "---":
            continue

        prev = lines[i - 1].strip() if i > 0 else ""
        # genuine setext heading: plain text directly above
        if prev and not prev.startswith(NOT_TEXT):
            continue

        nxt = next((lines[j].strip() for j in range(i + 1, len(lines)) if lines[j].strip()), "")
        hits.append(i + 1)
        if nxt.startswith("#"):
            drop.add(i)          # heading below already separates
        else:
            lines[i] = "***"

    if hits:
        touched.append((path, hits))
        if apply_fix:
            out = [l for n, l in enumerate(lines) if n not in drop]
            open(path, "w", encoding="utf-8").write("\n".join(out))

if not touched:
    print("Nothing left to fix.")
else:
    verb = "fixed" if apply_fix else "would fix"
    total = sum(len(h) for _, h in touched)
    print(f"{verb} {total} dividers across {len(touched)} files"
          + ("" if apply_fix else "  (run with --fix to apply)") + "\n")
    for p, h in touched:
        print(f"  {p}  lines {', '.join(str(n) for n in h[:10])}"
              + (f" ... +{len(h)-10} more" if len(h) > 10 else ""))
