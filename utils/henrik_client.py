import os

import aiohttp

BASE_URL = "https://api.henrikdev.xyz"


class HenrikClient:
    """Thin async wrapper around the HenrikDev Valorant API."""

    def __init__(self):
        self.api_key = os.getenv("HENRIK_API_KEY", "")

    def _headers(self):
        return {"Authorization": self.api_key} if self.api_key else {}

    async def _get(self, path: str):
        url = f"{BASE_URL}{path}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self._headers()) as resp:
                data = await resp.json()
                return resp.status, data

    async def get_account(self, name: str, tag: str):
        return await self._get(f"/valorant/v2/account/{name}/{tag}")

    async def get_mmr(self, region: str, name: str, tag: str):
        return await self._get(f"/valorant/v2/mmr/{region}/{name}/{tag}")

    async def get_match_history(self, region: str, name: str, tag: str):
        return await self._get(f"/valorant/v3/matches/{region}/{name}/{tag}")