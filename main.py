# Importing the discord library, the commands module, and the tasks module from discord.ext.
import discord
from discord.ext import tasks
from discord.ext import commands

# Importing the os module and the load_dotenv function from the dotenv module.
import os
from dotenv import load_dotenv

# Importing the datetime modules for calculating the time.
# import datetime
# from datetime import timedelta

load_dotenv()

# Setting up the client with intents.
intents = discord.Intents.default()
intents.message_content = True

# This is a subclass of client that provides a command tree automatically.
# The command prefix is the character that triggers the command, the intents
# are the intents that the bot will use, and the application_id is required
# for the bot to sync slash commands (https://discordpy.readthedocs.io/en/stable/interactions/api.html#discord.app_commands.CommandTree.sync).
bot = commands.Bot(
    command_prefix="/", intents=intents, application_id=int(os.getenv("APPLICATION_ID"))
)


@bot.event
async def on_ready():
    # Load all the cogs in the cogs folder.
    try:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await bot.load_extension(
                    f"cogs.{filename[:-3]}"
                )  # Strips the file extension.
    except Exception as e:
        print(f"Error loading extension: {e}")

    # Sync the slash commands with discord.
    try:
        synced_commands = await bot.tree.sync()
        print(
            f"Synced {len(synced_commands)} command(s)"
        )  # If the sync is successful, this will print the number of commands synced.
    except Exception as e:
        print(f"Commands could not be synced: {e}")

    print(f"We have logged in as {bot.user}")


bot.run(os.getenv("TOKEN"))
