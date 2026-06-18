import anthropic
from app.config import ANTHROPIC_API_KEY

client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are a professional GitHub assistant acting on behalf of a developer.
Your job is to write helpful, concise, and technically accurate replies to GitHub issues, pull requests, and comments.
- Be professional and friendly
- Keep responses focused and to the point
- If it's a bug report, acknowledge it and ask clarifying questions if needed
- If it's a PR, summarize what you understand from the description and mention next steps
- If it's a mention/question, answer it directly
- Never pretend to have merged, deployed, or done anything you haven't actually done
- Always write in the same language as the issue/comment (French or English)
"""


async def ask_claude(context: str) -> str:
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": context}],
    )
    return response.content[0].text
