import random
from typing import Optional, List, Union

from ..API.api import DANBORRU_BASE_URL
from ..Client.Client import client, DEFAULT_HEADERS

class Danbooru:
    @staticmethod
    async def fetch_images(tag: Optional[str] = None, limit: int = 1) -> Union[str, List[str], None]:
        """
        Fetch image URLs from Danbooru API based on a tag.
        """
        request_limit = 200 if limit == 1 else limit
        
        params = {"limit": request_limit, "page": random.randint(1, 50)}
        
        if tag:
            params["tags"] = tag.replace(" ", "_")

        try:
            response = await client.get(DANBORRU_BASE_URL, params=params, headers=DEFAULT_HEADERS)
            response.raise_for_status()
            images = response.json()
            if not isinstance(images, list):
                return None

            file_urls = [img["file_url"] for img in images if "file_url" in img]
            if not file_urls:
                return None

            if limit == 1:
                return random.choice(file_urls)
            else:
                return file_urls[:limit]
        except Exception as e:
            print(f"Error fetching images: {e}")
            return None
