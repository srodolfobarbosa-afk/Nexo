import os
import subprocess
import tempfile
import logging
from datetime import datetime

logger = logging.getLogger("auto_builder")


def create_autobuild_branch(base_branch: str = "main") -> str:
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    branch = f"autobuild/{ts}"
    subprocess.check_call(["git", "checkout", "-b", branch, base_branch])
    return branch


def commit_and_push(branch: str, message: str) -> str:
    subprocess.check_call(["git", "add", "-A"]) 
    subprocess.check_call(["git", "commit", "-m", message])
    subprocess.check_call(["git", "push", "-u", "origin", branch])
    return branch


def create_pr(branch: str, title: str, body: str):
    # use gh CLI if available; otherwise output instructions
    try:
        subprocess.check_call(["gh", "pr", "create", "--title", title, "--body", body, "--head", branch])
        logger.info("PR created via gh CLI")
    except Exception:
        logger.info("gh CLI not available — please create PR manually")


def run_autobuild(patch_commands: list[str], dry_run: bool = True):
    base = "main"
    branch = create_autobuild_branch(base)
    try:
        for cmd in patch_commands:
            logger.info("Running patch command: %s", cmd)
            if not dry_run:
                subprocess.check_call(cmd, shell=True)
        msg = f"autobuild: apply patches {datetime.utcnow().isoformat()}"
        if not dry_run:
            commit_and_push(branch, msg)
            create_pr(branch, "Autobuild: proposed changes", "Automated patches applied. Run tests and review before merge.")
        else:
            logger.info("Dry run: no commits pushed. Branch %s created locally.", branch)
    except Exception as e:
        logger.exception("Autobuild failed: %s", e)
        raise
