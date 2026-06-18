import httpx
from app.config import GITHUB_TOKEN

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

BASE_URL = "https://api.github.com"


async def post_issue_comment(repo: str, issue_number: int, body: str):
    url = f"{BASE_URL}/repos/{repo}/issues/{issue_number}/comments"
    async with httpx.AsyncClient() as client:
        r = await client.post(url, headers=HEADERS, json={"body": body})
        r.raise_for_status()
    return r.json()


async def get_pr_diff(repo: str, pr_number: int) -> str:
    """Fetch PR diff for additional context (truncated to avoid token overflow)."""
    url = f"{BASE_URL}/repos/{repo}/pulls/{pr_number}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers={**HEADERS, "Accept": "application/vnd.github.diff"})
    diff = r.text
    # Truncate to avoid overloading Claude context
    return diff[:3000] + "\n...[diff truncated]" if len(diff) > 3000 else diff


async def get_issue_comments(repo: str, issue_number: int, limit: int = 5) -> list[dict]:
    """Fetch last N comments on an issue for context."""
    url = f"{BASE_URL}/repos/{repo}/issues/{issue_number}/comments"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=HEADERS, params={"per_page": limit})
    return r.json()
