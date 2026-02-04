import subprocess
import sys
from agent.sqlx_parser import parse_sqlx
from agent.rules import load_rules, validate_column
from agent.github_pr import post_pr_summary,build_summary
from agent.rules import suggest_column_name

rules = load_rules()
violations = {}

files = subprocess.check_output(
    ["git", "diff", "--name-only", "origin/main...HEAD"]
).decode().splitlines()

errors_found = False

for file in files:
    if not file.endswith(".sqlx"):
        continue

    with open(file) as f:
        sql = f.read()

    for col in parse_sqlx(sql):
        errors = validate_column(col, rules)

        if not errors:
            continue

        # -------- THIS IS WHERE VIOLATIONS ARE ASSIGNED --------

        if file not in violations:
            violations[file] = {}

        violations[file][col.name] = {
            "line": col.line_no,
            "errors": errors,
            "suggested": suggest_column_name(col)
        }

if violations:
    summary = build_summary(violations)
    post_pr_summary(summary)
    sys.exit(1)
    errors_found=True

if errors_found:
    print("❌ Naming violations found")
    sys.exit(1)

print("✅ All checks passed")
