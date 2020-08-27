import os
import random
import discord
from dotenv import load_dotenv
import sqlite3

# SQL Variable
SECONDS = 86400  # 24 hours in seconds


def StartSQL():
    connection = sqlite3.connect('triggy_users.db')

    c = connection.cursor()

    c.execute(
        f"CREATE TABLE IF NOT EXISTS users (Discord_User text PRIMARY KEY, Last_Daily_Call int, Next_Daily_Call int AS (Last_Daily_Call + {SECONDS}) )")
    return c

# Enter user into database. Note that last_daily call is initialized as 8 hours before the current time (allowing the user to call daily if they haven't.)


def InsertUserDB(temp_c: sqlite3.Cursor, DiscordUserName: str):
    # Check if user in database
    temp_c.execute(
        "SELECT Discord_User FROM users WHERE Discord_User = (?)", (str(DiscordUserName),))
    user = temp_c.fetchone()
    if not user:  # Not found, introduce
        temp_c.execute(
            "INSERT INTO users (Discord_User, Last_Daily_Call) VALUES((?), (SELECT strftime('%s','now')))", (str(DiscordUserName), ))
    else:  # Found user
        return


# Checks if the user can call triggy.daily


def CheckDaily(temp_c: sqlite3.Cursor, userIn: str) -> bool:
    # First, check if user in database
    temp_c.execute(
        "SELECT Discord_User FROM users WHERE Discord_User = (?)", (str(userIn),))
    user = temp_c.fetchone()
    if not user:  # User not in database, therefore: add them.
        InsertUserDB(temp_c, userIn)
        return True

    else:
        # User was found in database
        # Now, compare current time with Next_Daily_Call
        # explicit typing to convert date to seconds
        temp_c.execute(
            "SELECT Next_Daily_Call FROM users WHERE Discord_User = (?)", (str(userIn),))
        timeNext: int = temp_c.fetchone()
        temp_c.execute("SELECT strftime('%s','now')")
        timeNow: int = temp_c.fetchone()
        # Compare next_daily_call to current time
        if(timeNext[0] < int(timeNow[0])):
            return True
        else:
            return False


c = StartSQL()

with open("trigidentities.txt", 'r', encoding="UTF-8") as readFile:
    trig_identities = readFile.readlines()

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
server = os.getenv('DISCORD_GUILD')

client = discord.Client()


@ client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == server:
            break

    print(f'{client.user} has connected to Discord :)')
    print(f'{guild.name}')


@ client.event
async def on_message(message_req):

    if message_req.author == client.user:  # make sure the bot doesn't call itself, somehow
        return

    print(message_req.content.lower().strip())
    if message_req.content == 'triggy.daily':
        if(CheckDaily(c, message_req.author)):
            response = random.choice(trig_identities)
        else:
            response = "You must wait"
        await message_req.channel.send(response)
    elif message_req.content.lower().strip() == 'triggy.help':
        response = """Current Triggy Commands Are:
                    triggy.daily
                    -Sends you your daily trigonometric identity to learn.
                    triggy.help
                    -Sends list of commands
                    triggy are you alive?
                    -For testing purposes/connectivity.
                    """
        await message_req.channel.send(response)
    # For Discord testing purposes.
    elif message_req.content.lower().strip() == "triggy are you alive?":
        response = 'Yes, I am alive.'
        await message_req.channel.send(response)


client.run(token)
