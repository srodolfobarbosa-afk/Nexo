from ..agent import AgentRequest, run_agent
from ..llm import generate_text


def propose_change(repo: str, file_path: str, intent_description: str) -> dict:
    prompt = f"You are an assistant that proposes a change to the repository file {file_path}.\nTask: {intent_description}\nProvide the full new contents for the file."
    new_content = generate_text(prompt)
    # return a proposal (dry-run)
    return {"file_path": file_path, "proposed_content": new_content}


def propose_and_submit(
    repo: str, file_path: str, intent_description: str, auto_apply: bool = False
):
    proposal = propose_change(repo, file_path, intent_description)
    # If auto_apply True, use agent.run_agent to create PR (requires token and auto_apply)
    if auto_apply:
        req = AgentRequest(
            repo=repo,
            branch_prefix="autogen",
            file_path=file_path,
            file_content=proposal["proposed_content"],
            pr_title=f"Auto change: {file_path}",
            pr_body=intent_description,
            auto_apply=True,
        )
        return run_agent(req)
    return {"status": "proposal", "proposal": proposal}
