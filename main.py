import discord
import os
import requests
import time

from discord.ext import tasks
import datetime

# for .env file
from dotenv import load_dotenv


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
        return 3
    elif "goldstar" in darren:
        return 1
    elif "goldstar" in brandon:
        return 2
    else:
        return 0


def update_time_tracker_file(winner):
    with open("data/time_tracker.txt", "r+") as time_tracker_file:
        time_tracker_file.seek(0)
        time_tracker = [int(line) for line in time_tracker_file.read().splitlines()]

        match winner:
            case 0:  # neither have the badge
                time_tracker[0] = int(time.time())
                time_tracker[1] = int(time.time())
            case 1:  # darren has the badge
                time_tracker[1] = int(time.time())
            case 2:  # brandon has the badge
                time_tracker[0] = int(time.time())
            case 3:  # both have the badge
                pass

        time_tracker_file.seek(0)
        time_tracker_file.truncate()
        for item in time_tracker:
            time_tracker_file.write(f"{item}\n")


def forecast_message(winner):
    current_time = int(time.time())

    with open("data/time_tracker.txt", "r") as time_tracker_file:
        time_tracker_file.seek(0)
        time_tracker = [int(line) for line in time_tracker_file.read().splitlines()]

    match winner:
        case 0:
            print("Neither have the badge :(")
            return "Neither have the badge :("
        case 1:
            print(
                f"Only Darren has the badge! He has had it for {current_time - time_tracker[0]} seconds. :star:"
            )
            return f"Only Darren has the badge! He has had it for {current_time - time_tracker[0]} seconds. :star:"
        case 2:
            print(
                f"Only Brandon has the badge! He has had it for {current_time - time_tracker[1]} seconds. :star:"
            )
            return f"Only Brandon has the badge! He has had it for {current_time - time_tracker[1]} seconds. :star:"
        case 3:
            print("Both have the badge!")
            return "Both have the badge!"


def add_channel(message):
    with open("data/daily_channels.txt", "r+") as daily_channels_file:
        daily_channels_file.seek(0)
        daily_channels = [int(line) for line in daily_channels_file.read().splitlines()]

        if message.channel.id in daily_channels:
            return "Channel already in daily updates list."

        else:
            daily_channels.append(message.channel.id)
            for channel in daily_channels:
                daily_channels_file.write(f"{channel}\n")

            return "Added to daily updates list."


def remove_channel(message):
    with open("data/daily_channels.txt", "r+") as daily_channels_file:
        daily_channels_file.seek(0)
        daily_channels = [int(line) for line in daily_channels_file.read().splitlines()]

        if message.channel.id not in daily_channels:
            return "Channel not in daily updates list."

        # overwrites the file with the new list
        else:
            daily_channels.remove(message.channel.id)
            daily_channels_file.seek(0)
            daily_channels_file.truncate()
            for channel in daily_channels:
                daily_channels_file.write(f"{channel}\n")

            return "Removed from daily updates list."


load_dotenv()

# Check if the update file exists
if not os.path.exists("data/daily_channels.txt"):
    # If it doesn't exist, create it
    with open("data/daily_channels.txt", "w") as daily_channels_file:
        pass
# check if the time tracker file exists
if not os.path.exists("data/time_tracker.txt"):
    # If it doesn't exist, create it
    with open("data/time_tracker.txt", "w") as time_tracker_file:
        for i in range(0, 2):
            time_tracker_file.write(f"{int(time.time())}\n")

# sets up client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
daily_channels = []

client.run(os.getenv("TOKEN"))


# runs when the bot is ready
@client.event
async def on_ready():
    daily_update.start()
    update_time_tracker.start()
    print("We have logged in as {0.user}".format(client))


# runs when a message is sent
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$forecast"):
        winner = find_winner()
        update_time_tracker_file(winner)
        await message.channel.send(forecast_message(winner))

    # TODO: add a way to customize time
    if message.author.id == 391343816155725824:
        # adds the channel to the update list
        if message.content.startswith("$add"):
            await message.channel.send(add_channel(message))

        # removes a channel from the update list
        if message.content.startswith("$remove"):
            await message.channel.send(remove_channel(message))

        # kills program
        if message.content.startswith("$order66"):
            await client.close()


@tasks.loop(minutes=5)
async def update_time_tracker():
    update_time_tracker_file(find_winner())
    print("Updated time tracker file.")


# runs at 9AM everyday
@tasks.loop(time=datetime.time(hour=17, minute=0))
async def daily_update():
    # reads the channels to update from a file
    with open("data/daily_channels.txt", "r") as f:
        f.seek(0)
        daily_channels = [int(line) for line in f.read().splitlines()]

    print("Sending daily update...")

    winner = find_winner()
    update_time_tracker_file(winner)

    for channel in daily_channels:
        await client.get_channel(channel).send(
            "**Daily Update:**\n" + forecast_message(winner)
        )
        print(f"Sent daily update to channel {channel}.")

    print("Daily update finished!")
