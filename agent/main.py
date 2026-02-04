import subprocess
import sys
from agent.sqlx_parser import parse_sqlx
from agent.rules import load_rules, validate_column
from agent.github_pr import post_inline_comment
from agent.rules import suggest_column_name

rules = load_rules()

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

        if errors:
            errors_found = True
            suggested = suggest_column_name(col)

            error_text = "\n".join([f"- {e}" for e in errors])

            message = (
                f"❌ **{col.name}:**\n"
                f"{error_text}\n\n"
                f"💡 **Suggested name:** `{suggested}`"
            )

            post_inline_comment(
                file=file,
                line=col.line_no,
                message=message
            )

if errors_found:
    print("❌ Naming violations found")
    sys.exit(1)

print("✅ All checks passed")
