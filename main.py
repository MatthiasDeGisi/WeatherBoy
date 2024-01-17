import discord
import os

from discord.ext import tasks
import datetime

# for .env file
from dotenv import load_dotenv
load_dotenv()

#TODO: see if I can do it without writing to a file
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
update_channels = []

# runs when the bot is ready
@client.event
async def on_ready():
    daily_update.start()
    print("We have logged in as {0.user}".format(client))

# runs when a message is sent
@client.event
async def on_message(message):
    if message.author == client.user:
        return
        
    if message.content.startswith("$forecast"):
        await message.channel.send(find_winner())
    
    if message.author.id == 391343816155725824:
        
        if message.content.startswith("$add"):
            update_channels.append(message.channel.id)
            await message.channel.send("Added.")
            
        if message.content.startswith("$remove"):
            update_channels.remove(message.channel.id)
            await message.channel.send("Removed.")
        

# runs at 9AM everyday
@tasks.loop(time=datetime.time(hour=17, minute=0))
async def daily_update():
    for channel in update_channels:
        await client.get_channel(channel).send("Daily Update:\n" + find_winner())
  
client.run(os.getenv("TOKEN"))
