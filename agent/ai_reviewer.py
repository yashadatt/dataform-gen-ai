import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SYSTEM_PROMPT = """You are a strict Dataform PR naming reviewer.
Only review table and column naming quality.
Do not review SQL logic or performance.
Follow the naming conventions provided.
Do not invent issues. Return [] if no issues.
"""

USER_PROMPT_TEMPLATE = """Naming conventions:
{conventions}

Changed SQLX files:
{payload}

Detect:
- typos
- inconsistent abbreviations
- short vs long form mismatches
- same meaning with different names in the same file

Return JSON array:
[
  {{
    "file": "...",
    "column": "...",
    "issue_type": "typo | abbreviation | inconsistency | semantic_mismatch",
    "message": "...",
    "suggested_name": "...",
    "severity": "error | warning"
  }}
]
"""

def run_ai_review(payload: list, conventions: dict):
    user_prompt = USER_PROMPT_TEMPLATE.format(
        conventions=json.dumps(conventions, indent=2),
        payload=json.dumps(payload, indent=2)
    )

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0
    )

    content = resp.choices[0].message.content.strip()
    return json.loads(content)
