import logging
from app.config import GITHUB_USERNAME, BOT_NAME
from app.services.claude import ask_claude
from app.services.github import post_issue_comment, get_issue_comments
from app.services.slack import notify_slack

logger = logging.getLogger(__name__)

# Simple in-memory set to prevent bot from replying to itself
# For production: replace with Redis-backed deduplication
_processed_comment_ids: set[int] = set()


async def handle_mention(payload: dict):
    """@mention in an issue or PR comment."""
    comment = payload["comment"]
    issue = payload["issue"]
    repo = payload["repository"]["full_name"]
    commenter = comment["user"]["login"]
    comment_id = comment["id"]

    # Skip if already processed (idempotency)
    if comment_id in _processed_comment_ids:
        return
    _processed_comment_ids.add(comment_id)

    # Skip if the bot or you wrote this comment (loop prevention)
    if commenter in (GITHUB_USERNAME, BOT_NAME):
        return

    # Only respond if bot is mentioned
    body = comment["body"] or ""
    if f"@{BOT_NAME}" not in body and f"@{GITHUB_USERNAME}" not in body:
        return

    # Fetch last few comments for thread context
    recent_comments = await get_issue_comments(repo, issue["number"], limit=5)
    thread = "\n".join(
        [f"- @{c['user']['login']}: {c['body'][:200]}" for c in recent_comments]
    )

    context = f"""You were mentioned in a GitHub comment on `{repo}`.

Issue/PR title: {issue['title']}
Issue body: {issue['body'][:500] if issue.get('body') else '(none)'}

Recent thread:
{thread}

The comment that mentioned you (by @{commenter}):
{body}

Reply directly to the question or request in the mention. Be concise and helpful."""

    reply = await ask_claude(context)
    await post_issue_comment(repo, issue["number"], reply)

    await notify_slack(
        event_type="mention",
        repo=repo,
        title=f"#{issue['number']} {issue['title']}",
        url=comment["html_url"],
        claude_reply=reply,
    )
    logger.info(f"Handled mention in {repo}#{issue['number']} by @{commenter}")
