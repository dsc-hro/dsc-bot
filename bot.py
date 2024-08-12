import os
import logging
import json
import random
import datetime as dt
from zoneinfo import ZoneInfo

# dotenv to parse environment variables
import dotenv

import discord
from discord.ext import commands, tasks

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# load glados voice lines
responses = None

try:
    with open("portal_glados_lines.json", "r") as f:
        responses = json.load(f)
except FileNotFoundError:
    logger.warn("Couldn't find quotes file!")

# parse secrets from .env file
dotenv.load_dotenv()

# get secrets: while token is str, parse ids to int
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = int(os.getenv("GUILD"))
MAIN_CHANNEL = int(os.getenv("MAIN_CHANNEL"))
PIZZA_CHANNEL = int(os.getenv("PIZZA_CHANNEL"))
APP_ID = int(os.getenv("APP_ID"))

# prefix for bot commands
BOT_PREFIX = "$"

intents = discord.Intents.default()

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)


@bot.hybrid_command(name="cake", description="Definitely not a lie!")
async def cake(ctx):
    """Sends a random GladOS voiceline."""
    msg = "The cake is a lie!"
    if responses is not None:
        msg = random.choice(responses)
    if msg != "":
        await ctx.send(msg)

# target timezone
tz = ZoneInfo("Europe/Berlin")

# convert to system time
# pizza_time = dt.datetime.now("Europe/Berlin").replace(hour=9, minute=0, second=0).astimezone()
# logger.info("Pizza Time: %s", pizza_time)

# attendance_time = dt.datetime.now(tz).replace(hour=9, minute=0, second=0).astimezone()
# logger.info("Attendance Time: %s", attendance_time)

pizza_time = dt.time(hour=9, tzinfo=tz)
attendance_time = dt.time(hour=9, tzinfo=tz)


class PizzaCog(commands.Cog):
    """Runs a Pizza Poll every Monday."""

    def __init__(self, bot):
        self.bot = bot
        logger.info("starting pizza task")
        self.pizza_task.start()

    def cog_unload(self):
        self.pizza_task.cancel()

    @tasks.loop(time=pizza_time)
    async def pizza_task(self):
        # check if its monday
        monday = 0
        now = dt.datetime.now(tz)

        if dt.datetime.weekday(now) == monday:
            await self.pizza_poll()

    async def pizza_poll(self):
        logger.info("Here is the pizza pollice!")

        duration = dt.timedelta(hours=11)

        pizza_poll = discord.Poll(
            question="Ding dong, here is the Pizza-Pollice from Pizzapolis!",
            multiple=False,
            duration=duration
        )

        pizza_poll.add_answer(text="Vegan", emoji="\N{pineapple}")
        pizza_poll.add_answer(text="Vegetarian", emoji="\N{cheese wedge}")
        pizza_poll.add_answer(text="Carnivore", emoji="\N{bacon}")
        pizza_poll.add_answer(text="But I refuse!", emoji="\N{face with no good gesture}")

        channel = self.bot.get_channel(PIZZA_CHANNEL)
        await channel.send(poll=pizza_poll)


class AttendanceCog(commands.Cog):
    """Checks Attendance every Monday."""

    def __init__(self, bot):
        self.bot = bot
        logger.info("starting attendance task")
        self.attendance_task.start()

    def cog_unload(self):
        self.attendance_task.cancel()

    @tasks.loop(time=attendance_time)
    async def attendance_task(self):
        # check if its monday
        monday = 0
        now = dt.datetime.now(tz)

        if dt.datetime.weekday(now) == monday:
            await self.check_attendance()

    async def check_attendance(self):
        logger.info("checking attendance")

        duration = dt.timedelta(hours=10)

        attendance_poll = discord.Poll(
            question="Data is calling! My A.T.T.E.N.D.A.N.C.E module predicts that you:",
            multiple=False,
            duration=duration
        )

        attendance_poll.add_answer(text="will be there!", emoji="\N{heavy large circle}")
        attendance_poll.add_answer(text="won't join today!", emoji="\N{cross mark}")

        channel = self.bot.get_channel(MAIN_CHANNEL)
        await channel.send(poll=attendance_poll)


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    # add tasks to the bot
    await bot.add_cog(PizzaCog(bot))
    await bot.add_cog(AttendanceCog(bot))
    logger.info("Sync Command Tree")
    await bot.tree.sync()
    logger.info("Ready!")

if __name__ == "__main__":
    logger.addHandler(logging.StreamHandler())
    logger.addHandler(logging.FileHandler("bot.log"))
    logger.setLevel(logging.INFO)

    bot.run(TOKEN)
