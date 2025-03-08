import discord
import os
import requests
import time

from discord.ext import tasks
import datetime
from datetime import timedelta

# for .env file
from dotenv import load_dotenv


def change_manager():  # TODO: code this
    # find winner
    # determine if winner has changed
    # if winner has changed, dont update but save winner status
    # if winner has not changed, update time tracker?
    pass


def find_winner():
    """Find the winner of the gold star badge.

    Returns:
        str: The winner of the gold star badge.
    """

    response = requests.get("https://www.wunderground.com/dashboard/pws/IGABRI5")
    darren = response.text

    response = requests.get("https://www.wunderground.com/dashboard/pws/INANAI140")
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
    global winner_state
    global winner_state_change_counter
    
    if winner_state != winner:
        winner_state_change_counter += 1
        if winner_state_change_counter >= 3:
            winner_state = winner
            winner_state_change_counter = 0
    
    elif winner_state == winner:
        winner_state_change_counter = 0
    
    with open("data/time_tracker.txt", "r+") as time_tracker_file:
        time_tracker_file.seek(0)
        time_tracker = [int(line) for line in time_tracker_file.read().splitlines()]

        current_time = int(time.time())

        match winner_state:
            case 0:  # neither have the badge
                time_tracker[0] = current_time
                time_tracker[1] = current_time
            case 1:  # darren has the badge
                time_tracker[1] = current_time
            case 2:  # brandon has the badge
                time_tracker[0] = current_time
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
            return "Neither have the badge :("
        case 1:
            weeks, days, hours, minutes, seconds = convert_unix_time(
                current_time - time_tracker[0]
            )
            winner_names = ["Darren"]
            leading_string = "Only **Darren** has the badge!"
        case 2:
            weeks, days, hours, minutes, seconds = convert_unix_time(
                current_time - time_tracker[1]
            )
            winner_names = ["Brandon"]
            leading_string = "Only **Brandon** has the badge!"
        case 3:
            winner_names = ["Darren", "Brandon"]
            leading_string = "**Both** have the badge!"

    full_message = leading_string

    for name in winner_names:
        weeks, days, hours, minutes, seconds = convert_unix_time(
            current_time - time_tracker[0 if name == "Darren" else 1]
        )
        if weeks:
            full_message += f"\n{name} has had the badge for {weeks} week{'' if weeks == 1 else 's'}, {days} day{'' if days == 1 else 's'}, {hours} hours, {minutes} minutes, and {seconds} seconds."
        else:
            full_message += f"\n{name} has had the badge for {days} day{'' if days == 1 else 's'}, {hours} hours, {minutes} minutes, and {seconds} seconds."
            
    return full_message


def convert_unix_time(unix_time):
    # Convert Unix time to timedelta
    td = timedelta(seconds=unix_time)

    # Calculate time components
    weeks, days = divmod(td.days, 7)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return weeks, days, hours, minutes, seconds


def add_channel(message):
    with open("data/daily_channels.txt", "r+") as daily_channels_file:
        daily_channels_file.seek(0)
        daily_channels = [int(line) for line in daily_channels_file.read().splitlines()]

        if message.channel.id not in daily_channels:
            daily_channels.append(message.channel.id)
            for channel in daily_channels:
                daily_channels_file.write(f"{channel}\n")

            return "Added to daily updates list."

        else:
            return "Channel already in daily updates list."


def remove_channel(message):
    with open("data/daily_channels.txt", "r+") as daily_channels_file:
        daily_channels_file.seek(0)
        daily_channels = [int(line) for line in daily_channels_file.read().splitlines()]

        if message.channel.id in daily_channels:
            daily_channels.remove(message.channel.id)
            daily_channels_file.seek(0)
            daily_channels_file.truncate()
            for channel in daily_channels:
                daily_channels_file.write(f"{channel}\n")

            return "Removed from daily updates list."

        # overwrites the file with the new list
        else:
            return "Channel not in daily updates list."


load_dotenv()

# Check if the update file exists
if not os.path.exists("data/daily_channels.txt"):
    with open("data/daily_channels.txt", "w") as daily_channels_file:
        pass
# check if the time tracker file exists
if not os.path.exists("data/time_tracker.txt"):
    with open("data/time_tracker.txt", "w") as time_tracker_file:
        for i in range(0, 2):
            time_tracker_file.write(f"{int(time.time())}\n")

# sets up client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
daily_channels = []
winner_state = 0
winner_state_change_counter = 0

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


# runs at 9AM everyday
@tasks.loop(time=datetime.time(hour=16, minute=0))
async def daily_update():
    # reads the channels to update from a file
    with open("data/daily_channels.txt", "r") as f:
        f.seek(0)
        daily_channels = [int(line) for line in f.read().splitlines()]

    winner = find_winner()
    update_time_tracker_file(winner)

    for channel in daily_channels:
        await client.get_channel(channel).send(
            "**Daily Update:**\n" + forecast_message(winner)
        )


client.run(os.getenv("TOKEN"))
