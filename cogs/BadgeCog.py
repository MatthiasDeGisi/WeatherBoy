import discord
from discord import app_commands
from discord.ext import commands
from discord import tasks

# Import custom badgechecker class.
from classes import BadgeChecker

class BadgeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """Initializes the CheckBadge cog.

        Args:
            bot (commands.Bot): The bot that the cog is loaded into.
        """
        # This is a reference to the bot object that is passed in when the cog is loaded.
        self.bot = bot # May not be needed
        
        # Create a new BadgeChecker object and daily update manager.
        self.checker = BadgeChecker(bot.db)

    # This is a decorator that registers a new command under the bot. the .tree part
    # is needed for slash commands (app commands), as opposed to a regular prefix command.
    # https://discordpy.readthedocs.io/en/stable/interactions/api.html#discord.app_commands.Command
    # https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Command
    # name=... is the name of the command that will be used in Discord.
    @app_commands.command(name="addstation")
    async def add_station(
        self,
        interaction: discord.Interaction,
        station_id: str,
        first_name: str,
        last_name: str,  # These names must be all lowercase. Not exactly sure how come, just that discord.py throws me error codes.
    ):
        """Command to add a station to the Firestore database.

        Args:
            interaction (discord.Interaction): This is passed in by the discord.py library and is used to send messages back to the user.
            station_id (str): The ID of the station to add.
            first_name (str): First name of the station owner.
            last_name (str): Last name of the station owner.
        """
        try:
            self.checker.add_station(station_id, first_name, last_name)
            await interaction.response.send_message(
                f"Station {station_id} added with owner {first_name} {last_name}."
            )
        except Exception as e:
            await interaction.response.send_message(f"Error adding station: {e}")

    @app_commands.command(name="removestation")
    async def remove_station(self, interaction: discord.Interaction, station_id: str):
        """Command to remove a station from the Firestore database.

        Args:
            interaction (discord.Interaction): This is passed in by the discord.py library and is used to send messages back to the user.
            station_id (str): The ID of the station to remove.
        """
        try:
            self.checker.remove_station(station_id)
            await interaction.response.send_message(f"Station {station_id} removed.")
        except Exception as e:
            await interaction.response.send_message(f"Error removing station: {e}")
    
    @app_commands.command(name="forecast") #TODO
    async def forecast(self, interaction: discord.Interaction):
        """Command to get the status of all the stations.

        Args:
            interaction (discord.Interaction): This is passed in by the discord.py library and is used to send messages back to the user.
        """
        try:
            self.BadgeChecker.get_badge_status()
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}")

        @tasks.loop(minutes=20) #TODO
        async def scrape_and_write_badge_status():
            pass
        
async def setup(bot):
    """Setup function to add the cog as an extension. is used by the bot.load_extension() function. Must be async."""
    await bot.add_cog(BadgeCog(bot))