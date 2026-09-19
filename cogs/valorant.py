import discord
import io
import re
from typing import Optional
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from utils.henrik_client import HenrikClient
from utils.account_store import AccountStore


class Valorant(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = HenrikClient()
        self.accounts = AccountStore()

    async def resolve_riot_id(self, ctx: commands.Context, riot_id: Optional[str], region: str):
        """
        Returns (name, tag, region) or (None, None, None) if it couldn't be resolved
        (and already sent an error message to the user).

        riot_id can be "name#tag", a Discord @mention (uses that user's saved account),
        or None (uses the command author's saved account).
        """
        # @mention -> look up that user's saved account
        mention = re.fullmatch(r"<@!?(\d+)>", riot_id) if riot_id else None
        if mention:
            user_id = int(mention.group(1))
            target = next((m for m in ctx.message.mentions if m.id == user_id), None)
            who = target.display_name if target else "That user"
            account = await self.accounts.get_account(user_id)
            if not account:
                await ctx.send(
                    f"{who} hasn't set an account yet. They can use `!setaccount name#tag`."
                )
                return None, None, None
            return account["name"], account["tag"], account.get("region", region)

        if riot_id:
            if "#" not in riot_id:
                await ctx.send("Please use the format `name#tag`, e.g. `wad2k#jbc`.")
                return None, None, None
            name, tag = riot_id.split("#", 1)
            return name, tag, region

        # No riot_id passed — fall back to the user's saved account
        account = await self.accounts.get_account(ctx.author.id)
        if not account:
            await ctx.send(
                "You haven't set an account yet. Use `!setaccount name#tag` first, "
                "or pass one directly, e.g. `!rank wad2k#jbc`."
            )
            return None, None, None

        return account["name"], account["tag"], account.get("region", region)

    @commands.command(name="rank")
    async def rank(self, ctx: commands.Context, riot_id: Optional[str] = None, region: str = "eu"):
        """!rank [name#tag] [region]  e.g. !rank wad2k#jbc  |  or just !rank if you've set an account"""
        name, tag, region = await self.resolve_riot_id(ctx, riot_id, region)
        if name is None:
            return

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
    async def todayrr(self, ctx: commands.Context, riot_id: Optional[str] = None, region: str = "eu"):
        """!todayrr [name#tag] [region]  e.g. !todayrr wad2k#jbc  |  or just !todayrr if you've set an account"""
        name, tag, region = await self.resolve_riot_id(ctx, riot_id, region)
        if name is None:
            return

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

    @commands.command(name="recentgames")
    async def recentgames(
        self,
        ctx: commands.Context,
        riot_id: Optional[str] = None,
        region: str = "eu",
        count: int = 5,
    ):
        """!recentgames [name#tag] [region] [count]  e.g. !recentgames wad2k#jbc eu 8  |  or just !recentgames"""
        name, tag, region = await self.resolve_riot_id(ctx, riot_id, region)
        if name is None:
            return

        count = max(1, min(count, 10))  # keep it between 1 and 10

        # Change mode="competitive" to None to include every queue (unrated, deathmatch, etc.)
        status, data = await self.client.get_match_history(
            region, name, tag, mode="competitive", size=count
        )
        if status != 200:
            await ctx.send(f"Couldn't fetch recent games for `{name}#{tag}` (status {status}).")
            return

        matches = data.get("data", [])
        if not matches:
            await ctx.send(f"No recent competitive games found for `{name}#{tag}`.")
            return

        # RR changes live in a different endpoint, so grab them and match on match id.
        # If this call fails we just skip the RR part.
        rr_by_match = {}
        mmr_status, mmr_data = await self.client.get_mmr_history(region, name, tag)
        if mmr_status == 200:
            for g in mmr_data.get("data", {}).get("history", []):
                if g.get("match_id"):
                    rr_by_match[g["match_id"]] = g.get("last_change", 0)

        lines = []
        wins = losses = 0
        total_k = total_d = total_a = 0
        net_rr = 0
        have_rr = False

        for match in matches:
            meta = match.get("metadata", {})
            players = match.get("players", {}).get("all_players", [])

            me = next(
                (
                    p for p in players
                    if p.get("name", "").lower() == name.lower()
                    and p.get("tag", "").lower() == tag.lower()
                ),
                None,
            )
            if me is None:
                continue

            stats = me.get("stats", {})
            kills = stats.get("kills", 0)
            deaths = stats.get("deaths", 0)
            assists = stats.get("assists", 0)
            total_k += kills
            total_d += deaths
            total_a += assists
            game_kd = kills / max(deaths, 1)

            team = me.get("team", "").lower()
            team_info = match.get("teams", {}).get(team, {})
            rounds_won = team_info.get("rounds_won", 0)
            rounds_lost = team_info.get("rounds_lost", 0)

            if team_info.get("has_won"):
                emoji = "🟢"
                wins += 1
            elif rounds_won == rounds_lost:
                emoji = "⬜"  # draw
            else:
                emoji = "🔴"
                losses += 1

            map_name = meta.get("map", "Unknown")
            agent = me.get("character", "Unknown")
            line = (
                f"{emoji} **{map_name}** — {agent} • "
                f"**{kills}/{deaths}/{assists}** ({game_kd:.2f} K/D) • "
                f"{rounds_won}-{rounds_lost}"
            )

            change = rr_by_match.get(meta.get("matchid"))
            if change is not None:
                have_rr = True
                net_rr += change
                sign = "+" if change > 0 else ""
                line += f" • {sign}{change} RR"

            start = meta.get("game_start")
            if start:
                line += f" • <t:{int(start)}:R>"

            lines.append(line)

        if not lines:
            await ctx.send(f"Couldn't find `{name}#{tag}` in the returned matches.")
            return

        kd = total_k / max(total_d, 1)
        footer = f"{wins}W {losses}L • {kd:.2f} K/D"
        if have_rr:
            net_sign = "+" if net_rr >= 0 else ""
            footer += f" • Net {net_sign}{net_rr} RR"

        embed = discord.Embed(
            title=f"{name}#{tag} — Last {len(lines)} Games",
            description="\n".join(lines),
            color=discord.Color.green() if wins >= losses else discord.Color.red(),
        )
        embed.set_footer(text=footer)

        await ctx.send(embed=embed)

    @commands.command(name="crosshair")
    async def crosshair(self, ctx: commands.Context, *, code: str):
        """!crosshair <code> e.g. !crosshair 0;P;h;0;0l;5;0v;3;0g;1;0o;2;0a;1;0f;0;1b;0"""
        try:
            status, data = await self.client.get_crosshair(code)
        except Exception as e:
            await ctx.send(f"Error fetching crosshair: {e}")
            raise

        if status != 200:
            await ctx.send(f"Couldn't fetch crosshair` (status {status}).")
            return

        file = discord.File(io.BytesIO(data), filename="crosshair.png")
        embed = discord.Embed(title="Crosshair Preview")
        embed.set_image(url="attachment://crosshair.png")
        await ctx.send(embed=embed, file=file)

    @commands.command(name="setaccount")
    async def setaccount(self, ctx: commands.Context, riot_id: str, region: str = "eu"):
        """!setaccount <name>#<tag> [region]  e.g. !setaccount wad2k#jbc"""
        if "#" not in riot_id:
            await ctx.send("Please use the format `name#tag`, e.g. `wad2k#jbc`.")
            return

        name, tag = riot_id.split("#", 1)

        # Optional: validate the account actually exists before saving it
        status, _ = await self.client.get_mmr(region, name, tag)
        if status != 200:
            await ctx.send(
                f"Couldn't verify `{name}#{tag}` in region `{region}` (status {status}). "
                "Account not saved — double check the name/tag/region."
            )
            return

        await self.accounts.set_account(ctx.author.id, name, tag, region)
        await ctx.send(f"✅ Account set to `{name}#{tag}` ({region}). Future commands will use this by default.")

    @commands.command(name="myaccount")
    async def myaccount(self, ctx: commands.Context):
        """!myaccount  — shows the account you've saved"""
        account = await self.accounts.get_account(ctx.author.id)
        if not account:
            await ctx.send("You haven't set an account yet. Use `!setaccount name#tag`.")
            return
        await ctx.send(f"Your saved account: `{account['name']}#{account['tag']}` ({account.get('region', 'eu')})")

    @commands.command(name="clearaccount")
    async def clearaccount(self, ctx: commands.Context):
        """!clearaccount  — removes your saved account"""
        removed = await self.accounts.clear_account(ctx.author.id)
        if removed:
            await ctx.send("Your saved account has been removed.")
        else:
            await ctx.send("You don't have an account set.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Valorant(bot))