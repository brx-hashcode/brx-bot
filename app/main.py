import hmac
import hashlib
import json
import logging

from fastapi import FastAPI, Request, Header, HTTPException
from app.handlers.issue import handle_issue_opened, handle_issue_assigned
from app.handlers.pr import handle_pr_assigned
from app.handlers.comment import handle_mention

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GitHub Bot")


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/github/webhook")
async def webhook(
    request: Request,
    x_github_event: str = Header(...),
    x_hub_signature_256: str = Header(...),
):
    from app.config import WEBHOOK_SECRET

    body = await request.body()

    if not verify_signature(body, x_hub_signature_256, WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = json.loads(body)
    action = payload.get("action", "")

    logger.info(f"Event: {x_github_event} | Action: {action}")

    # Issue opened in your repos
    if x_github_event == "issues" and action == "opened":
        await handle_issue_opened(payload)

    # Issue assigned to you
    elif x_github_event == "issues" and action == "assigned":
        await handle_issue_assigned(payload)

    # PR assigned to you
    elif x_github_event == "pull_request" and action == "assigned":
        await handle_pr_assigned(payload)

    # @mention in any comment (issue or PR)
    elif x_github_event == "issue_comment" and action == "created":
        await handle_mention(payload)

    return {"ok": True}
