import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from utils.henrik_client import HenrikClient


class Valorant(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = HenrikClient()

    @commands.command(name="rank")
    async def rank(self, ctx: commands.Context, riot_id: str, region: str = "eu"):
        """!rank <name>#<tag> [region]  e.g. !rank wad2k#jbc"""
        if "#" not in riot_id:
            await ctx.send("Please use the format `name#tag`, e.g. `wad2k#jbc`.")
            return

        name, tag = riot_id.split("#", 1)

        status, data = await self.client.get_mmr(region, name, tag)
    
        if status != 200:
            await ctx.send(f"Couldn't fetch rank for `{name}#{tag}` (status {status}).")
            return

        current = data.get("data", {}).get("current_data", {})
        tier_name = current.get("currenttierpatched", "Unranked")
        rr = current.get("ranking_in_tier", 0)

        embed = discord.Embed(
            title=f"{name}#{tag}",
            description=f"**{tier_name}** — {rr} RR",
            color=discord.Color.red(),
        )
        icon = current.get("images", {}).get("small")
        if icon:
            embed.set_thumbnail(url=icon)

        await ctx.send(embed=embed)

    @commands.command(name="todayrr")
    async def todayrr(self, ctx: commands.Context, riot_id: str, region: str = "eu"):
        """!todayrr <name>#<tag> [region]  e.g. !todayrr wad2k#jbc"""
        if "#" not in riot_id:
            await ctx.send("Please use the format `name#tag`, e.g. `wad2k#jbc`.")
            return

        name, tag = riot_id.split("#", 1)

        status, data = await self.client.get_mmr_history(region, name, tag)
    
        if status != 200:
            await ctx.send(f"Couldn't fetch RR history for `{name}#{tag}` (status {status}).")
            return

        history = data.get("data", {}).get("history", [])
        if not history:
            await ctx.send("No match history found.")
            return

        cutoff = datetime.now(timezone.utc) - timedelta(hours=14)
        todays_games = []
        for game in history:
            game_date_str = game.get("date")
            if not game_date_str:
                continue
            game_time = datetime.fromisoformat(game_date_str.replace("Z", "+00:00"))
            if game_time >= cutoff:
                todays_games.append(game)

        if not todays_games:
            await ctx.send(f"No games played today for `{name}#{tag}`.")
            return

        net_rr = sum(g.get("last_change", 0) for g in todays_games)
        wins = sum(1 for g in todays_games if g.get("last_change", 0) > 0)
        losses = sum(1 for g in todays_games if g.get("last_change", 0) < 0)

        sign = "+" if net_rr >= 0 else ""
        embed = discord.Embed(
            title=f"{name}#{tag} — Today's RR",
            description=f"**{sign}{net_rr} RR** across {len(todays_games)} games ({wins}W {losses}L)",
            color=discord.Color.green() if net_rr >= 0 else discord.Color.red(),
        )

        await ctx.send(embed=embed)




async def setup(bot: commands.Bot):
    await bot.add_cog(Valorant(bot))