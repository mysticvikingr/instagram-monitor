import httpx
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

BASE_URL = settings.TIKHUB_API_BASE_URL
TOKEN = settings.TIKHUB_API_KEY

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

async def fetch_from_tikhub(endpoint: str, params: dict) -> dict | None:
    if not TOKEN:
        logger.warning("Tikhub API token is not set. Please update it in your .env file.")
        return None

    url = f"{BASE_URL}{endpoint}"
    logger.info(f"Making request to Tikhub API: URL={url}, Params={params}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, headers=headers, timeout=60.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while fetching from Tikhub: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error("An unexpected error occurred while fetching from Tikhub.", exc_info=True)
            return None 