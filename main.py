import logging, discord, os, asyncio
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="DDC.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

#set command prefix for discord
bot = commands.Bot(command_prefix="!!",intents=intents)

#notification to the terminal that bot is running
@bot.event
async def on_ready():
    print(f"we are ready to go in, {bot.user.name}")

#check how many slash commands have been synced
#syncronizes / commands
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} commands")
    except Exception as e:
        print(e)

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            print(f"loading {filename}")
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load()
        await bot.start(token)

asyncio.run(main())