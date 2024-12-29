import discord
from discord.ext import tasks
from discord.ext import commands


# Import custom badgechecker class.
from classes import BadgeChecker

# Importing the datetime modules for calculating the time.
import datetime
from datetime import timedelta

class DailyUpdateCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """Initializes the CheckBadge cog.

        Args:
            bot (commands.Bot): The bot that the cog is loaded into.
        """
        # This is a reference to the bot object that is passed in when the cog is loaded.
        self.bot = bot

    @tasks.loop(time=datetime.time(hour=16, minute=0)) #TODO: finish this and make the datetime not static.
    async def daily_update():
        pass

async def setup(bot):
    """Setup function to add the cog as an extension. is used by the bot.load_extension() function. Must be async."""
    await bot.add_cog(DailyUpdateCog(bot))