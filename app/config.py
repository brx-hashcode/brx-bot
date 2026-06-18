import os
from dotenv import load_dotenv

load_dotenv()

# GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")          # Personal Access Token or GitHub App token
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")       # GitHub App webhook secret
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")     # Your GitHub username (to detect assignments/mentions)
BOT_NAME = os.getenv("BOT_NAME", "github-bot")    # Bot name used in @mentions

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Slack
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")  # Slack Incoming Webhook URL
