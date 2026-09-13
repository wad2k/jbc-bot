# utils/account_store.py
import json
import os
import asyncio

class AccountStore:
    def __init__(self, path="data/accounts.json"):
        self.path = path
        self._lock = asyncio.Lock()
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump({}, f)

    def _read(self):
        with open(self.path, "r") as f:
            return json.load(f)

    def _write(self, data):
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

    async def set_account(self, discord_id: int, name: str, tag: str, region: str):
        async with self._lock:
            data = self._read()
            data[str(discord_id)] = {"name": name, "tag": tag, "region": region}
            self._write(data)

    async def get_account(self, discord_id: int):
        async with self._lock:
            data = self._read()
            return data.get(str(discord_id))

    async def clear_account(self, discord_id: int):
        async with self._lock:
            data = self._read()
            if str(discord_id) in data:
                del data[str(discord_id)]
                self._write(data)
                return True
            return False