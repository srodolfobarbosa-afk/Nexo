from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .agent import AgentRequest, run_agent

app = FastAPI(title="Autoconstructor Orchestrator")


class Intent(BaseModel):
    repo: str
    branch_prefix: str = "auto"
    file_path: str
    file_content: str
    pr_title: str
    pr_body: str | None = None
    auto_apply: bool = True


@app.post("/intents")
async def handle_intent(intent: Intent):
    # Run the agent to create branch and PR; agent will check for GITHUB_TOKEN
    req = AgentRequest(
        repo=intent.repo,
        branch_prefix=intent.branch_prefix,
        file_path=intent.file_path,
        file_content=intent.file_content,
        pr_title=intent.pr_title,
        pr_body=intent.pr_body,
        # auto_apply indicates whether the agent should actually create the PR (requires GITHUB_TOKEN)
        auto_apply=intent.auto_apply,
    )
    try:
        result = run_agent(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result
