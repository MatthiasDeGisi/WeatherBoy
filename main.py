import discord
import os

from discord.ext import tasks
import datetime

# for .env file
from dotenv import load_dotenv
load_dotenv()


def find_winner():
    """Find the winner of the gold star badge.

    Returns:
        str: The winner of the gold star badge.
    """
    os.system("curl -o output.txt https://www.wunderground.com/dashboard/pws/IGABRI5")


    with open("output.txt", "r", errors="replace") as f:
        darren = f.read()

    os.system("curl -o output.txt https://www.wunderground.com/dashboard/pws/IEXTEN1")

    with open("output.txt", "r+", errors="replace") as f:
        brandon = f.read()
        
        f.seek(0)
        f.truncate() 

    if "goldstar" in darren and "goldstar" in brandon:
        return "Both have the badge!"
    elif "goldstar" in darren:
        return "Only Darren has the badge!"
    elif "goldstar" in brandon:
        return "Only Brandon has the badge!"
    else:
        return "Both are slacking :("


# sets up client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# runs when the bot is ready
@client.event
async def on_ready():
    daily_update.start()
    print("We have logged in as {0.user}".format(client))

# runs when a message "$forecast" is sent
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$forecast"):
        await message.channel.send(find_winner())


# runs at 9AM everyday
@tasks.loop(time=datetime.time(hour=17, minute=0))
async def daily_update():
    channel = client.get_channel(1144885293426688102)
    await channel.send("Daily Update:\n" + find_winner())
  
client.run(os.getenv("TOKEN"))
