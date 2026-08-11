import discord
from discord.ext import commands
from datetime import datetime
from zoneinfo import ZoneInfo

from utils.football_client import FootballClient

CHELSEA_TEAM_ID = 61


class Football(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = FootballClient()

    @commands.command(name="nextmatch")
    async def next_match(self, ctx: commands.Context):
        """!nextmatch — shows Chelsea's next scheduled match"""
        status, data = await self.client.get_team_matches(
            CHELSEA_TEAM_ID, status="SCHEDULED", limit=1
        )

        if status != 200:
            await ctx.send(f"Couldn't fetch upcoming matches (status {status}).")
            return

        matches = data.get("matches", [])
        if not matches:
            await ctx.send("No upcoming matches found.")
            return

        match = matches[0]
        home = match.get("homeTeam", {}).get("name", "Unknown")
        away = match.get("awayTeam", {}).get("name", "Unknown")
        competition = match.get("competition", {}).get("name", "Unknown")
        kickoff_raw = match.get("utcDate")
        if kickoff_raw:
            utc_time = datetime.fromisoformat(kickoff_raw.replace("Z", "+00:00"))
            uk_time = utc_time.astimezone(ZoneInfo("Europe/London"))
            kickoff = uk_time.strftime("%A %d %B %Y, %H:%M")
        else:
            kickoff = "Unknown"

        embed = discord.Embed(
            title=f"{home} vs {away}",
            description=f"**Competition:** {competition}\n**Kickoff:** {kickoff}",
            color=discord.Color.blue(),
        )

        await ctx.send(embed=embed)

    @commands.command(name="lastresult")
    async def last_result(self, ctx: commands.Context):
        """!lastresult — shows Chelsea's most recent finished match"""
        status, data = await self.client.get_team_matches(
            CHELSEA_TEAM_ID, status="FINISHED", limit=1
        )

        if status != 200:
            await ctx.send(f"Couldn't fetch recent matches (status {status}).")
            return

        matches = data.get("matches", [])
        if not matches:
            await ctx.send("No recent matches found.")
            return

        match = matches[-1]  # most recent finished match is last in the list
        home = match.get("homeTeam", {}).get("name", "Unknown")
        away = match.get("awayTeam", {}).get("name", "Unknown")
        score = match.get("score", {}).get("fullTime", {})
        home_score = score.get("home", "?")
        away_score = score.get("away", "?")
        competition = match.get("competition", {}).get("name", "Unknown")

        embed = discord.Embed(
            title=f"{home} {home_score} - {away_score} {away}",
            description=f"**Competition:** {competition}",
            color=discord.Color.green(),
        )

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Football(bot))