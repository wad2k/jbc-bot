import asyncio
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

INITIAL_EXTENSIONS = [
    "cogs.valorant",
    "cogs.football",
]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.strip().lower() == "jbc bot":
        await message.channel.send("hi")

    if message.content.strip().lower() == "ano":
        await message.channel.send("hello ano")

    if message.content.strip().lower() == "vookum":
            await message.channel.send("AI LONDON OPEN THAT SHIT UP")

    await bot.process_commands(message)


async def main():
    async with bot:
        for extension in INITIAL_EXTENSIONS:
            await bot.load_extension(extension)
        await bot.start(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    asyncio.run(main())