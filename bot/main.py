# Copyright 2025 Niklas Glienke

import discord
from discord.ext import commands, tasks
from textwrap import dedent
from dotenv import load_dotenv
import logging
import os
import time
import csv
import random

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
channelId = int(os.getenv("DISCORD_CHANNEL"))

handler = logging.FileHandler(filename="cvw22-operations-officer.log")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
global previousMinute
leftBrevityTerms = {}


def getMinute():
    return int(time.strftime("%M", time.gmtime()))


def getBrevityTerm():
    global leftBrevityTerms

    if len(leftBrevityTerms) <= 0:
        with open("brevityTerms.csv", mode="r") as f:
            reader = csv.DictReader(f, delimiter=",")

            for line in reader:
                leftBrevityTerms.update({line["Brevity"]: line["Description"]})

    listBT = list(leftBrevityTerms.keys())
    randomId = random.randrange(0, len(listBT))
    brevityTerm = listBT[randomId]
    description = leftBrevityTerms[brevityTerm]
    description = "\n".join(f"> {line}" for line in description.strip().splitlines())
    leftBrevityTerms.pop(brevityTerm)

    return dedent(
        f"""
        **Today, we're looking at the following Brevity Term:** `{brevityTerm}`
        {description}
        """)


@bot.event
async def on_ready():
    global previousMinute

    print(f"{bot.user.name} is now online!")
    previousMinute = getMinute() - 1
    scheduler.start()


@tasks.loop(seconds=1)
async def scheduler():
    global previousMinute
    currentMinute = getMinute()

    if not previousMinute >= currentMinute:

        channel = bot.get_channel(channelId)
        await channel.send(getBrevityTerm())
        previousMinute = currentMinute


@scheduler.before_loop
async def before_scheduler():
    await bot.wait_until_ready()


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
