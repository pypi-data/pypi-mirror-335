import random
from typing import Optional, List

from ..API.api import KONACHAN_BASE_URL
from ..Client.Client import client

class Konachan:
    @staticmethod
    async def fetch_images(tag: Optional[str] = None, limit: int = 1, max_retries: int = 10) -> List[str]:
        """
        Fetch image URLs from Konachan.
        """
        params = {"limit": 500} if limit == 1 else {"limit": limit}
        if tag:
            params["tags"] = tag

        attempt = 0
        while attempt < max_retries:
            try:
                response = await client.get(KONACHAN_BASE_URL, params=params)
                response.raise_for_status()

                if not response.content:
                    attempt += 1
                    continue

                images = response.json()
                if not isinstance(images, list):
                    attempt += 1
                    continue

                file_urls = [img["file_url"] for img in images if "file_url" in img]

                if limit == 1:
                    if not file_urls:
                        attempt += 1
                        continue
                    return [random.choice(file_urls)]
                else:
                    return file_urls[:limit]
            except Exception:
                attempt += 1
        return []

    @staticmethod
    async def fetch_sfw_images(tag: Optional[str] = None, limit: int = 1, max_retries: int = 10) -> List[str]:
        """
        Fetch safe-for-work images 
        """
        if tag:
            processed_tag = tag.replace(" ", "_")
            combined_tag = f"rating:safe {processed_tag}"
        else:
            combined_tag = "rating:safe"
        return await Konachan.fetch_images(tag=combined_tag, limit=limit, max_retries=max_retries)

    @staticmethod
    async def fetch_nsfw_images(tag: Optional[str] = None, limit: int = 1, max_retries: int = 10) -> List[str]:
        """
        Fetch not-safe-for-work images 
        """
        if tag:
            processed_tag = tag.replace(" ", "_")
            combined_tag = f"rating:explicit {processed_tag}"
        else:
            combined_tag = "rating:explicit"
        return await Konachan.fetch_images(tag=combined_tag, limit=limit, max_retries=max_retries)