import logging
from app.config import GITHUB_USERNAME
from app.services.claude import ask_claude
from app.services.github import post_issue_comment, get_pr_diff, post_pr_review
from app.services.slack import notify_slack

logger = logging.getLogger(__name__)


async def handle_pr_review_requested(payload: dict):
    """Review requested from you on a PR — Claude reviews the diff and posts a review."""
    pr = payload["pull_request"]
    repo = payload["repository"]["full_name"]
    requested_reviewer = payload.get("requested_reviewer", {}).get("login", "")

    if requested_reviewer != GITHUB_USERNAME:
        return

    diff = await get_pr_diff(repo, pr["number"])

    context = f"""You are a code reviewer. You have been asked to review a Pull Request in `{repo}`.

PR title: {pr['title']}
Author: @{pr['user']['login']}
Base branch: {pr['base']['ref']} ← {pr['head']['ref']}
PR description:
{pr['body'] or '(no description provided)'}

Diff:
{diff}

Write a thorough but concise code review. Cover:
- Correctness: any bugs or logic errors
- Code quality: readability, naming, structure
- Security: any obvious vulnerabilities
- Suggestions: specific improvements with examples if helpful

End with a clear verdict: APPROVE if the code looks good, or REQUEST CHANGES if there are issues that must be fixed before merging."""

    reply = await ask_claude(context)

    # Determine approval based on Claude's verdict
    approved = reply.upper().find("APPROVE") > reply.upper().find("REQUEST CHANGES") if "REQUEST CHANGES" in reply.upper() else "APPROVE" in reply.upper()
    event = "APPROVE" if approved else "REQUEST_CHANGES"

    await post_pr_review(repo, pr["number"], reply, event)

    await notify_slack(
        event_type="pr_assigned",
        repo=repo,
        title=f"PR #{pr['number']} {pr['title']}",
        url=pr["html_url"],
        claude_reply=reply,
    )
    logger.info(f"Handled pr_review_requested: {repo}#{pr['number']} — {event}")


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
