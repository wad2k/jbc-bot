import os

import aiohttp

BASE_URL = "https://api.football-data.org/v4"


class FootballClient:
    """Thin async wrapper around the football-data.org API."""

    def __init__(self):
        self.api_key = os.getenv("FOOTBALL_API_KEY", "")

    def _headers(self):
        return {"X-Auth-Token": self.api_key}

    async def _get(self, path: str):
        url = f"{BASE_URL}{path}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self._headers()) as resp:
                data = await resp.json()
                return resp.status, data

    async def get_team_matches(self, team_id: int, status: str = "SCHEDULED", limit: int = 5):
        return await self._get(f"/teams/{team_id}/matches?status={status}&limit={limit}")