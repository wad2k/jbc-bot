"""
Quick sanity check for the HenrikDev Valorant API.
Run this locally (not in a sandboxed/offline environment) to confirm the API is live.

1. Get a free "Basic" key: join the HenrikDev support Discord, then generate a key at
   https://api.henrikdev.xyz/dashboard/
2. Put it in a .env file as HENRIK_API_KEY=your_key_here (or just paste it below for testing)
3. pip install requests python-dotenv
4. python test_henrik_api.py
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HENRIK_API_KEY", "")
HEADERS = {"Authorization": API_KEY} if API_KEY else {}

BASE_URL = "https://api.henrikdev.xyz"


def test_status():
    """Check VALORANT server status for EU region - simple no-name-needed endpoint."""
    url = f"{BASE_URL}/valorant/v1/status/eu"
    r = requests.get(url, headers=HEADERS, timeout=10)
    print(f"[status] {r.status_code} -> {r.text[:300]}")


def test_account(name: str, tag: str):
    """Look up a known public account."""
    url = f"{BASE_URL}/valorant/v2/account/{name}/{tag}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    print(f"[account] {r.status_code} -> {r.text[:500]}")


if __name__ == "__main__":
    print("Testing HenrikDev API...\n")
    test_status()
    print()
    # TenZ is a well-known public pro player account, good for testing
    test_account("wad2k", "jbc")