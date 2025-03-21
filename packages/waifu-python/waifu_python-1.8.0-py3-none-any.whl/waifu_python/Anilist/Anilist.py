##TESTING
import random
import re
from typing import Optional, Dict, Any, List

from ..Client.Client import client
from ..API.api import GRAPHQL_BASE_URL 

class Anilist:
    @staticmethod
    async def get_characters(query: str, variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch characters from Anilist GraphQL API."""
        try:
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            response = await client.post(GRAPHQL_BASE_URL, headers=headers, json={"query": query, "variables": variables})
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("Page", {}).get("characters", [])
        except Exception as e:
            print(f"Error fetching characters: {e}")
            return []

    @staticmethod
    async def get_characters_list(limit: int = 50, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch characters sorted by popularity, optionally filtered by search."""
        query = """
        query ($page: Int, $perPage: Int, $search: String) {
          Page(page: $page, perPage: $perPage) {
            characters(sort: FAVOURITES_DESC, search: $search) {
              id
              name { full }
              gender
              age
              description
              image { large }
              media { edges { node { title { romaji } } } }
            }
          }
        }
        """
        variables = {"page": 1, "perPage": limit, "search": search}
        return await Anilist.get_characters(query, variables)

    @staticmethod
    async def get_waifus(limit: int = 50, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch female characters."""
        characters = await Anilist.get_characters_list(limit, search)
        return [char for char in characters if char.get("gender", "").lower() == "female"]

    @staticmethod
    def clean_description(description: str) -> str:
        """Clean the character's description."""
        if not description:
            return "No description available."
        cleaned = re.sub(r'(<br>|\*\*|__)', '', description)
        return cleaned.strip()

    @staticmethod
    async def fetch_waifus(count: int = 3, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get multiple random waifus."""
        waifus = await Anilist.get_waifus(search=search)
        if not waifus:
            return []
        return [Anilist._process_character(w) for w in random.sample(waifus, min(count, len(waifus)))]

    @staticmethod
    async def fetch_characters(count: int = 3, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get multiple random characters."""
        characters = await Anilist.get_characters_list(search=search)
        if not characters:
            return []
        return [Anilist._process_character(c) for c in random.sample(characters, min(count, len(characters)))]

    @staticmethod
    def _process_character(character: Dict[str, Any]) -> Dict[str, Any]:
        """Process character data to extract info."""
        media = character.get("media", {}).get("edges", [])
        titles = list({m["node"]["title"]["romaji"] for m in media if m.get("node", {}).get("title")})
        anime_title = Anilist._process_titles(titles) if titles else "Unknown"

        return {
            "name": character["name"]["full"],
            "image": character["image"]["large"],
            "age": character.get("age", "Unknown"),
            "gender": character.get("gender", "Unknown"),
            "description": Anilist.clean_description(character.get("description", "")),
            "anime": anime_title
        }

    @staticmethod
    def _process_titles(titles: List[str]) -> str:
        """Simplify anime titles by removing common suffixes."""
        processed = [re.sub(r'\s*(?:Season|Part|Cour|Saga|Arc|:|\().*', '', t).strip() for t in titles]
        unique = list(dict.fromkeys(processed))
        return unique[0] if unique else titles[0]
