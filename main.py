import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True

from PIL import Image
import io

ASCII_CHARS = "@%#*+=-:. "

def preprocess_image(image, new_width=45):
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width * 0.55)
    image = image.resize((new_width, new_height))
    return image.convert("L")

def image_to_ascii(image):
    image = preprocess_image(image)
    pixels = image.getdata()

    chars = [
        ASCII_CHARS[pixel * len(ASCII_CHARS) // 256]
        for pixel in pixels
    ]

    ascii_str = "".join(chars)
    width = image.width

    return "\n".join(
        ascii_str[i:i+width]
        for i in range(0, len(ascii_str), width)
    )

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'we are ready to go in', {bot.user.name})

@bot.event
async def on_message(message):
    print("MESSAGE RECEIVED:", message.content)
    if message.author == bot.user:
        return

    if "<:robloxemoji:1315835149476171776>" in message.content:
        print("roblox emoji detected")
        await message.channel.send("<:robloxemoji:1315835149476171776>")

    if "😭🙏" in message.content:
        await message.channel.send("choski, is that you?")

    if "june bug cult" in message.content:
        await message.channel.send("june bug cult")

    # $ascii command (reply-based)
    if message.content.strip() == "$ascii":
        if not message.reference:
            await message.reply("Reply to an image with `$ascii`.")
            return

        replied = await message.channel.fetch_message(
            message.reference.message_id
        )

        if not replied.attachments:
            await message.reply("That message has no image.")
            return

        attachment = replied.attachments[0]

        if not attachment.content_type or not attachment.content_type.startswith("image/"):
            await message.reply("That attachment is not an image.")
            return

        data = await attachment.read()
        image = Image.open(io.BytesIO(data))

        ascii_art = image_to_ascii(image)
        ascii_art = ascii_art[:1900]  # Discord limit

        await message.channel.send(f"```\n{ascii_art}\n```")
        return



    await bot.process_commands(message)



bot.run(token, log_handler=handler,log_level=logging.DEBUG)




