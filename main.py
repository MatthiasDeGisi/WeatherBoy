# Import custom badgechecker class.
from classes import BadgeChecker

# Importing the discord library, the commands module, and the tasks module from discord.ext.
import discord
from discord.ext import tasks
from discord.ext import commands

# Importing the os module and the load_dotenv function from the dotenv module.
import os
from dotenv import load_dotenv

# Importing the datetime modules for calculating the time.
import datetime
from datetime import timedelta

load_dotenv()

# Creating an instance of the BadgeChecker class.
checker = BadgeChecker()

# Setting up the client with intents.
intents = discord.Intents.default()
intents.message_content = True

# This is a subclass of client that provides a command processing system.
# The command prefix is the character that triggers the command, the intents
# are the intents that the bot will use, and the application_id is required
# for the bot to sync slash commands (https://discordpy.readthedocs.io/en/stable/interactions/api.html#discord.app_commands.CommandTree.sync).
bot = commands.Bot(
    command_prefix="/", intents=intents, application_id=int(os.getenv("APPLICATION_ID"))
)


@bot.event
async def on_ready():
    # Sync the slash commands with discord.
    try:
        synced_commands = await bot.tree.sync()
        print(
            f"Synced {len(synced_commands)} command(s)"
        )  # If the sync is successful, this will print the number of commands synced.
    except Exception as e:
        print(f"Commands could not be synced: {e}")

    print(f"We have logged in as {bot.user}")


# This is a decorator that registers a new command under the bot. the .tree part
# is needed for slash commands (app commands), as opposed to a regular prefix command.
# https://discordpy.readthedocs.io/en/stable/interactions/api.html#discord.app_commands.Command
# https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Command
# name=... is the name of the command that will be used in Discord.
@bot.tree.command(name="addstation")
async def add_station(
    interaction: discord.Interaction,
    station_id: str,
    first_name: str,
    last_name: str,  # These names must be all lowercase. Not exactly sure how come, just that discord.py throws me error codes..
):
    try:
        checker.add_station(station_id, first_name, last_name)
        await interaction.response.send_message(
            f"Station {station_id} added with owner {first_name} {last_name}."
        )
    except Exception as e:
        await interaction.response.send_message(f"Error adding station: {e}")


bot.run(os.getenv("TOKEN"))
