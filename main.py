import discord
import os
import requests
import time

from discord.ext import tasks
import datetime

# TODO: set up github actions workflow to remove .env file
# for .env file
from dotenv import load_dotenv

load_dotenv()


def find_winner():
    """Find the winner of the gold star badge.

    Returns:
        str: The winner of the gold star badge.
    """

    print("Requesting data...")

    response = requests.get("https://www.wunderground.com/dashboard/pws/IGABRI5")
    darren = response.text

    response = requests.get("https://www.wunderground.com/dashboard/pws/IEXTEN1")
    brandon = response.text

    if "goldstar" in darren and "goldstar" in brandon:
        print("Both have the badge!")
        return "Both have the badge!"

    elif "goldstar" in darren:
        print("Only Darren has the badge!")
        return "Only Darren has the badge!"

    elif "goldstar" in brandon:
        print("Only Brandon has the badge!")
        return "Only Brandon has the badge!"

    else:
        print("Neither have the badge :(")
        return "Neither have the badge :("


# Check if the update file exists
if not os.path.exists("data/update_channels.txt"):
    # If it doesn't exist, create it
    with open("data/update_channels.txt", "w") as update_channels_file:
        pass
#TODO  
if not os.path.exists("data/time_tracker.txt"):
    # If it doesn't exist, create it
    with open("data/time_tracker.txt", "w") as time_tracker_file:
        for i in range(0, 2):
            time_tracker_file.write("0\n")
            time_tracker_file.write(f"{int(time.time())}\n")
    
# sets up client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
update_channels = []


# runs when the bot is ready
@client.event
async def on_ready():
    daily_update.start()
    time_tracker.start()
    print("We have logged in as {0.user}".format(client))


# runs when a message is sent
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$forecast"):
        await message.channel.send(find_winner())

    # TODO: add a way to customize time
    if message.author.id == 391343816155725824:
        # adds the channel to the update list
        if message.content.startswith("$add"):
            with open("data/update_channels.txt", "r+") as update_channels_file:
                update_channels_file.seek(0)
                update_channels = [int(line) for line in update_channels_file.read().splitlines()]

                if message.channel.id in update_channels:
                    await message.channel.send("Channel already in daily updates list.")
                    print("Channel already in daily updates list.")

                else:
                    update_channels.append(message.channel.id)
                    for channel in update_channels:
                        update_channels_file.write(f"{channel}\n")

                    await message.channel.send("Added to daily updates list.")
                    print(f"Channel {message.channel.id} added to daily updates list.")

        # removes a channel from the update list
        if message.content.startswith("$remove"):
            # gets the update list
            with open("data/update_channels.txt", "r+") as update_channels_file:
                update_channels_file.seek(0)
                update_channels = [int(line) for line in update_channels_file.read().splitlines()]

                if message.channel.id not in update_channels:
                    await message.channel.send("Channel not in daily updates list.")
                    print("Channel not in daily updates list.")

                # overwrites the file with the new list
                else:
                    update_channels.remove(message.channel.id)
                    update_channels_file.seek(0)
                    update_channels_file.truncate()
                    for channel in update_channels:
                        update_channels_file.write(f"{channel}\n")

                    await message.channel.send("Removed from daily updates list.")
                    print(
                        f"Channel {message.channel.id} removed from daily updates list."
                    )

        # kills program
        if message.content.startswith("$order66"):
            await client.close()

@tasks.loop(minutes=5)
async def time_tracker():
    with open ("data/time_tracker.txt", "r+") as time_tracker_file:
        time_tracker_file.seek(0)

# runs at 9AM everyday
@tasks.loop(time=datetime.time(hour=17, minute=0))
async def daily_update():
    # reads the channels to update from a file
    with open("data/update_channels.txt", "r") as f:
        f.seek(0)
        update_channels = [int(line) for line in f.read().splitlines()]

    print("Sending daily update...")
    for channel in update_channels:
        await client.get_channel(channel).send("**Daily Update:**\n" + find_winner())
        print(f"Sent daily update to channel {channel}.")

    print("Daily update finished!")


client.run(os.getenv("TOKEN"))
