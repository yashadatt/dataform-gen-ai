from github import Github
import os

def post_inline_comment(file, line, message):
    gh = Github(os.environ["GITHUB_TOKEN"])
    repo = gh.get_repo(os.environ["GITHUB_REPOSITORY"])
    pr = repo.get_pull(int(os.environ["PR_NUMBER"]))

    # Get latest commit in the PR
    commits = list(pr.get_commits())
    commit_sha = commits[-1].sha

    pr.create_review_comment(
        body=message,
        commit=commit_sha,
        path=file,
        line=line,
        side="RIGHT"
    )

def post_pr_summary(message):
    gh = Github(os.environ["GITHUB_TOKEN"])
    repo = gh.get_repo(os.environ["GITHUB_REPOSITORY"])
    pr = repo.get_pull(int(os.environ["PR_NUMBER"]))
    pr.create_issue_comment(message)

def build_summary(violations):
    lines = ["❌ **Dataform Naming Violations Found**\n"]

    for file, cols in violations.items():
        lines.append(f"📄 `{file}`\n")
        for col, info in cols.items():
            lines.append(f"• **{col}**")
            for e in info["errors"]:
                lines.append(f"  - {e}")
            lines.append(f"  💡 Suggested: `{info['suggested']}`\n")

    return "\n".join(lines)
