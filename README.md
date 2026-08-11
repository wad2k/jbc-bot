# JBC Discord Bot

A Discord bot with Valorant and football (Chelsea FC) integrations, built with `discord.py`.

## Setup

### 1. Clone and install dependencies

```bash
git clone [git@github.com:wad2k/jbc-bot.git](https://github.com/wad2k/jbc-bot.git)
cd discord-bot
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Environment variables

Create a `.env` file in the project root (this is gitignored — never commit it):

```
DISCORD_TOKEN=your_discord_bot_token
HENRIK_API_KEY=your_henrikdev_api_key
FOOTBALL_API_KEY=your_football_data_org_api_key
```

- **Discord token**: from the [Discord Developer Portal](https://discord.com/developers/applications)
- **HenrikDev key**: get a free "Basic" key via their support Discord → https://api.henrikdev.xyz/dashboard/
- **football-data.org key**: register free at https://www.football-data.org/client/register
