import logging
from app.config import GITHUB_USERNAME
from app.services.claude import ask_claude
from app.services.github import post_issue_comment, get_pr_diff
from app.services.slack import notify_slack

logger = logging.getLogger(__name__)


async def handle_pr_assigned(payload: dict):
    """PR assigned to you for review or action."""
    pr = payload["pull_request"]
    repo = payload["repository"]["full_name"]
    assignee = payload.get("assignee", {}).get("login", "")

    if assignee != GITHUB_USERNAME:
        return

    # Fetch the diff for richer context
    diff = await get_pr_diff(repo, pr["number"])

    context = f"""You have been assigned to a Pull Request in `{repo}`.

PR title: {pr['title']}
Author: @{pr['user']['login']}
Base branch: {pr['base']['ref']} ← {pr['head']['ref']}
PR description:
{pr['body'] or '(no description provided)'}

Diff preview:
{diff}

Write a short comment acknowledging the PR assignment. Summarize what you understand 
from the description and diff, and mention that you'll review it. Keep it concise."""

    reply = await ask_claude(context)

    # Post as a comment on the PR (PRs use the issues comment endpoint)
    await post_issue_comment(repo, pr["number"], reply)

    await notify_slack(
        event_type="pr_assigned",
        repo=repo,
        title=f"PR #{pr['number']} {pr['title']}",
        url=pr["html_url"],
        claude_reply=reply,
    )
    logger.info(f"Handled pr_assigned: {repo}#{pr['number']}")
