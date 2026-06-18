import httpx
import logging
from app.config import SLACK_WEBHOOK_URL

logger = logging.getLogger(__name__)


async def notify_slack(event_type: str, repo: str, title: str, url: str, claude_reply: str):
    """Send a Slack notification after Claude acts on a GitHub event."""
    if not SLACK_WEBHOOK_URL:
        logger.warning("SLACK_WEBHOOK_URL not set, skipping Slack notification")
        return

    # Truncate Claude reply preview for Slack
    preview = claude_reply[:300] + "..." if len(claude_reply) > 300 else claude_reply

    emoji_map = {
        "issue_opened": "🆕",
        "issue_assigned": "📋",
        "pr_assigned": "🔀",
        "mention": "💬",
    }
    emoji = emoji_map.get(event_type, "🤖")

    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} GitHub Bot acted on your behalf",
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Event:*\n{event_type.replace('_', ' ').title()}"},
                    {"type": "mrkdwn", "text": f"*Repo:*\n`{repo}`"},
                ],
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{title}*\n<{url}|View on GitHub>"},
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Claude replied:*\n```{preview}```",
                },
            },
        ]
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(SLACK_WEBHOOK_URL, json=payload)
        if r.status_code != 200:
            logger.error(f"Slack notification failed: {r.text}")
