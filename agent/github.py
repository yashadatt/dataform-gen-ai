from github import Github
import os

def post_inline_comment(file, line, message):
    gh = Github(os.environ["GITHUB_TOKEN"])
    repo = gh.get_repo(os.environ["GITHUB_REPOSITORY"])
    pr = repo.get_pull(int(os.environ["PR_NUMBER"]))

    pr.create_review_comment(
        body=message,
        path=file,
        line=line
    )