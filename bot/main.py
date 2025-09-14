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
import json
import numpy as np

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
channelBrevityId = int(os.getenv("DISCORD_CHANNEL_BREVITY"))
channelReportId = int(os.getenv("DISCORD_CHANNEL_REPORT"))

handler = logging.FileHandler(filename="cvw22-operations-officer.log")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
dailyBotTask = datetime.time(hour=11)
allBrevity = {}
leftBrevity = {}
lastDate = datetime.datetime.now().strftime("%d.%m.%Y")
with open("brevityTerms.csv", "r") as f:
    reader = csv.DictReader(f, delimiter=",")

    for line in reader:
        allBrevity.update({line["Brevity"]: line["Description"]})
with open("data.json") as f:
    data = json.load(f)


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


def createDayBrief():
    date = datetime.datetime.now()
    msg = "__Daybrief - " + date.strftime("%d.%m.%Y") + "__\n\n"
    msg = msg + "**Instrument approaches in use:** \n\n"

    for airport in data["airports"]:

        msg = msg + ("__" + airport["name"] + ":__" + "\n\n")
        for rwy in airport["approaches"]:
            rn = random.randint(1, len(rwy) - 1)
            msg = msg + rwy[0] + ": " + rwy[rn] + "\n"
        msg = msg + "\n"

    msg = msg + "**Callsigns of the day:** \n\n"
    cs_day = np.random.choice(data["callsigns"], size=4, replace=False)

    for callsign in cs_day:
        msg = msg + '_"' + callsign + '"_\n'

    msg = msg + "\n**Todays server IP is:\n\n**" + getIp()

    return msg


def createMonthlyRecap(pilots):
    return "Hello"


global lastBrief
lastBrief = createDayBrief()


@bot.event
async def on_ready():
    print(f"{bot.user.name} is now online!")
    sendDailyBrevity.start()
    sendMonthlyReport.start()


@tasks.loop(time=dailyBotTask)
async def sendDailyBrevity():
    channel = bot.get_channel(channelBrevityId)
    brevity = await getBrevity()
    await channel.send(brevity)


@tasks.loop(seconds=5)
async def sendMonthlyReport():
    currentMonth = int(datetime.datetime.now().strftime("%m"))
    with open("data.json", "r") as f:
        content = json.load(f)

    if content["previousMonth"] < currentMonth:
        channel = bot.get_channel(channelReportId)
        pilots = channel.members

        content["previousMonth"] = currentMonth

        with open("data.json", "w") as f:
            json.dump(content, f)
        await channel.send(createMonthlyRecap(pilots))


@sendDailyBrevity.before_loop
async def before_scheduler():
    await bot.wait_until_ready()


@bot.event
async def on_raw_reaction_add(payload):
    cID = str(payload.channel_id)
    channel = bot.get_channel(int(cID))

    msg = await channel.fetch_message(payload.message_id)
    if payload.emoji.name == "🖊️" and payload.member.name != "vCVW-22 Bot":
        msg_content = msg.content
        lines = msg_content.split("\n")
        i = 0
        cs_line_num = 0
        for line in lines:
            if "Callsigns of the day:" in line:
                cs_line_num = i + 2
            elif "~ signed by" in lines[cs_line_num]:
                if cs_line_num + 1 <= len(lines):
                    cs_line_num = cs_line_num + 1
            else:
                i = i + 1

        lines[cs_line_num] = lines[cs_line_num] + " ~ signed by " + payload.member.mention

        await msg.edit(content="\n".join(lines))
    elif payload.emoji.name == "📃" and payload.member.name != "vCVW-22 Bot":
        msg_content = msg.content
        lines = msg_content.split("\n")
        n = 0
        cs_line_num = 0
        for line in lines:
            if payload.member.mention in line:
                cs_line_num = n
                lines[n] = lines[n].split(" ~")[0]
                await msg.edit(content="\n".join(lines))
            else:
                n = n + 1


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
        global lastBrief

        if datetime.datetime.now().strftime("%d.%m.%Y") == lastDate:
            await message.channel.send(lastBrief)
        else:
            newBrief = createDayBrief()
            await message.channel.send(newBrief)
            lastBrief = newBrief
        lastmsg = await message.channel.fetch_message(message.channel.last_message_id)
        await lastmsg.add_reaction("🖊️")
        await lastmsg.add_reaction("📃")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
