import discord
from discord.ext import commands

from utils.henrik_client import HenrikClient


class Valorant(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = HenrikClient()

    @commands.command(name="rank")
    async def rank(self, ctx: commands.Context, name: str, tag: str, region: str = "eu"):
        """!rank <name> <tag> [region]  e.g. !rank wad2k jbc eu"""
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


async def setup(bot: commands.Bot):
    await bot.add_cog(Valorant(bot))