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
