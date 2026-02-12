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
from agent.ai_reviewer import run_ai_review
import yaml
def format_ai_violations(violations):
    lines = ["🤖 **AI Naming Review Failed**\n"]
    for v in violations:
        lines.append(
            f"📄 `{v['file']}` → `{v['column']}`\n"
            f"  - {v['message']}\n"
            f"  💡 Suggested: `{v['suggested_name']}`\n"
        )
    return "\n".join(lines)

def extract_for_ai(files):
    payload = []
    for file in files:
        if not file.endswith(".sqlx"):
            continue
        with open(file) as f:
            sql = f.read()

        cols = parse_sqlx(sql)
        payload.append({
            "file": file,
            "table": file.split("/")[-1].replace(".sqlx", ""),
            "columns": [c.name for c in cols]
        })
    return payload

# after deterministic check block:

payload = extract_for_ai(files)

if payload:
    with open("rules/naming.yml") as f:
        conventions = yaml.safe_load(f)

    ai_violations = run_ai_review(payload, conventions)

    if ai_violations:
        post_pr_summary(format_ai_violations(ai_violations))
        raise SystemExit("❌ AI naming checks failed")


if violations:
    summary = build_summary(violations)
    post_pr_summary(summary)
    sys.exit(1)
    errors_found=True

if errors_found:
    print("❌ Naming violations found")
    sys.exit(1)

print("✅ All checks passed")
