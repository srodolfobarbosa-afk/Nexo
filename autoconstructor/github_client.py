import os
from github import Github


def get_github_client():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return None
    return Github(token)


def create_branch_and_pr(repo_full_name: str, branch_name: str, file_path: str, content: str, pr_title: str, pr_body: str | None = None):
    gh = get_github_client()
    if gh is None:
        return {"status": "dry-run", "message": "GITHUB_TOKEN not set; running in dry-run mode."}

    repo = gh.get_repo(repo_full_name)
    # create branch from default branch
    default_branch = repo.default_branch
    sb = repo.get_branch(default_branch)
    ref = f"refs/heads/{branch_name}"
    try:
        repo.create_git_ref(ref, sb.commit.sha)
    except Exception:
        # branch may already exist
        pass

    # create or update file
    try:
        contents = repo.get_contents(file_path, ref=branch_name)
        repo.update_file(contents.path, f"Update {file_path}", content, contents.sha, branch=branch_name)
    except Exception:
        repo.create_file(file_path, f"Add {file_path}", content, branch=branch_name)

    pr = repo.create_pull(title=pr_title, body=pr_body or "Automated PR", head=branch_name, base=default_branch)
    return {"status": "ok", "pr_url": pr.html_url}
