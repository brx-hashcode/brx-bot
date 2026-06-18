import asyncio
import logging
import httpx
import os

logger = logging.getLogger(__name__)

RENDER_URL = os.getenv("RENDER_URL", "")


async def keep_alive():
    if not RENDER_URL:
        logger.warning("RENDER_URL not set, keep-alive cron disabled")
        return

    url = f"{RENDER_URL.rstrip('/')}/health"
    while True:
        await asyncio.sleep(15 * 60)
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(url, timeout=10)
            logger.info(f"Keep-alive ping: {r.status_code}")
        except Exception as e:
            logger.error(f"Keep-alive ping failed: {e}")
