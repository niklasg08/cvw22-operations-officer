# Copyright 2025 Niklas Glienke

import discord
from discord.ext import commands, tasks
from textwrap import dedent
from dotenv import load_dotenv
import logging
import os
import datetime
import csv
import random
import urllib.request

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
channelBrevityId = int(os.getenv("DISCORD_CHANNEL_BREVITY"))

handler = logging.FileHandler(filename="cvw22-operations-officer.log")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
dailyBotTask = datetime.time(hour=11)
allBrevity = {}
leftBrevity = {}
with open("brevityTerms.csv", "r") as f:
    reader = csv.DictReader(f, delimiter=",")

    for line in reader:
        allBrevity.update({line["Brevity"]: line["Description"]})


def getIp():
    ip = urllib.request.urlopen('https://v4.ident.me/').read().decode('utf8')
    return ip


async def getBrevity(searchedBrevity=None):
    global leftBrevity

    if searchedBrevity is None:
        if len(leftBrevity) <= 0:
            leftBrevity = allBrevity.copy()

        listBrevity = list(leftBrevity.keys())
        randomId = random.randrange(0, len(listBrevity))
        brevityTerm = listBrevity[randomId]
        description = leftBrevity[brevityTerm]
        description = "\n".join(f"> {line}" for line in description.strip().splitlines())
        leftBrevity.pop(brevityTerm)

        return dedent(f"""
                      **Today, we're looking at the following Brevity Term:** "{brevityTerm}"
                      {description}
                      """)
    else:
        results = []

        for brevity, description in allBrevity.items():
            if searchedBrevity.upper() in brevity.upper():
                results.append((brevity, description))

        for result in results:
            description = "\n".join(f"> {line}" for line in result[1].strip().splitlines())

            channel = bot.get_channel(channelBrevityId)
            await channel.send(dedent(f"""
                                     **Brevity Term:** "{result[0]}"
                                     {description}"""))


@bot.event
async def on_ready():
    print(f"{bot.user.name} is now online!")
    sendDailyBrevity.start()


@tasks.loop(time=dailyBotTask)
async def sendDailyBrevity():
    channel = bot.get_channel(channelBrevityId)
    brevity = await getBrevity()
    await channel.send(brevity)


@sendDailyBrevity.before_loop
async def before_scheduler():
    await bot.wait_until_ready()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mention in message.content.split():
        await message.channel.send("Good morning aviators!")

    if message.content.startswith("!test"):
        await message.channel.send("Hello World!")

    if message.content.startswith("!ip"):
        ip = getIp()
        await message.channel.send(ip)

    if message.content.startswith("!brevity"):
        brevity = message.content.replace("!brevity", "").strip()
        await getBrevity(brevity)

    if message.content.startswith("!daybrief"):
        await message.channel.send("The daybrief command isn't available atm!")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
