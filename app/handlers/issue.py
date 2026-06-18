import logging
from app.config import GITHUB_USERNAME
from app.services.claude import ask_claude
from app.services.github import post_issue_comment
from app.services.slack import notify_slack

logger = logging.getLogger(__name__)


async def handle_issue_opened(payload: dict):
    """New issue opened in one of your repos."""
    issue = payload["issue"]
    repo = payload["repository"]["full_name"]
    opener = issue["user"]["login"]

    # Skip if you opened it yourself
    if opener == GITHUB_USERNAME:
        return

    context = f"""A new GitHub issue was opened in the repository `{repo}`.

Issue title: {issue['title']}
Opened by: @{opener}
Issue body:
{issue['body'] or '(no description provided)'}

Write a friendly acknowledgement comment. Thank the reporter, confirm you've seen it, 
and ask any clarifying questions if the description is vague."""

    reply = await ask_claude(context)
    await post_issue_comment(repo, issue["number"], reply)

    await notify_slack(
        event_type="issue_opened",
        repo=repo,
        title=f"#{issue['number']} {issue['title']}",
        url=issue["html_url"],
        claude_reply=reply,
    )
    logger.info(f"Handled issue_opened: {repo}#{issue['number']}")


async def handle_issue_assigned(payload: dict):
    """Issue assigned to you."""
    issue = payload["issue"]
    repo = payload["repository"]["full_name"]
    assignee = payload.get("assignee", {}).get("login", "")

    # Only act if you are the one being assigned
    if assignee != GITHUB_USERNAME:
        return

    context = f"""You have been assigned to a GitHub issue in `{repo}`.

Issue title: {issue['title']}
Issue body:
{issue['body'] or '(no description provided)'}

Write a short comment acknowledging the assignment. Mention that you'll look into it 
and give a rough idea of next steps if you can infer them from the description."""

    reply = await ask_claude(context)
    await post_issue_comment(repo, issue["number"], reply)

    await notify_slack(
        event_type="issue_assigned",
        repo=repo,
        title=f"#{issue['number']} {issue['title']}",
        url=issue["html_url"],
        claude_reply=reply,
    )
    logger.info(f"Handled issue_assigned: {repo}#{issue['number']}")
