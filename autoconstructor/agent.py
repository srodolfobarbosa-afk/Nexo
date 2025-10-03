from dataclasses import dataclass
from .github_client import create_branch_and_pr
import time


@dataclass
class AgentRequest:
    repo: str
    branch_prefix: str
    file_path: str
    file_content: str
    pr_title: str
    pr_body: str | None = None


def run_agent(req: AgentRequest):
    # create a unique branch name
    ts = int(time.time())
    branch_name = f"{req.branch_prefix}-{ts}"
    # call github client (will be dry-run if no token provided)
    result = create_branch_and_pr(req.repo, branch_name, req.file_path, req.file_content, req.pr_title, req.pr_body)
    return {"branch": branch_name, "result": result}
