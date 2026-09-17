"""
Finds .qmd files whose YAML front matter is never closed, and repairs them.

An unclosed front matter block makes Quarto read the page body as configuration,
which is what produces errors like:
    YAMLException: unidentified alias "*The"

Run with no arguments to see what would change:
    python3 check-and-fix-frontmatter.py

Run with --fix to apply the repair:
    python3 check-and-fix-frontmatter.py --fix
"""
import glob, sys

apply_fix = "--fix" in sys.argv
broken, ok, no_fm = [], [], []

for path in sorted(glob.glob("*.qmd")):
    lines = open(path, encoding="utf-8").read().split("\n")

    if not lines or lines[0].strip() != "---":
        no_fm.append(path)
        continue

    close = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), None)
    # a valid block has no blank line before its closing fence
    if close is not None and all(l.strip() for l in lines[1:close]):
        ok.append(path)
        continue

    broken.append(path)
    if apply_fix:
        end = next((i for i, l in enumerate(lines[1:], 1) if not l.strip()), len(lines))
        lines.insert(end, "---")
        open(path, "w", encoding="utf-8").write("\n".join(lines))

print(f"{len(ok)} fine | {len(broken)} unclosed | {len(no_fm)} no front matter at all\n")

if broken:
    print("UNCLOSED FRONT MATTER" + (" (repaired)" if apply_fix else " (run with --fix to repair)"))
    for p in broken:
        print("   ", p)
    print()

if no_fm:
    print("NO FRONT MATTER — fix these by hand, they need a --- title --- block on line 1")
    for p in no_fm:
        print("   ", p)
    print()

if not broken and not no_fm:
    print("Nothing to fix.")
