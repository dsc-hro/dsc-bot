#!/usr/bin/env bash

"""
Discord bot for the Data Science Club Rostock.

COMMANDS:

- /cake
    - Portal easteregg, will return a randomly chosen GlaDOS voiceline

TASKS:

- attendance:
    - on the day of the Data Science Club, the bot will post the attendance poll
- pizza:
    - on the day of the Data Science Club, the bot will post the pizza poll
"""


import asyncio
import os
import logging
import json
import random
import datetime as dt
import dataclasses as dc
# dotenv to parse environment variables
import dotenv
# discord.py provides the Python Discord API
import discord

from discord.ext import commands, tasks
from zoneinfo import ZoneInfo
from enum import IntEnum

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class WeekDay(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


@dc.dataclass
class Config:
    dsc_weekday: int = 1
    dsc_time: str = "17:00"

    dsc_poll_weekday: int = 1
    dsc_poll_time: str = "16:00"
    dsc_tz: str = "Europe/Berlin"


def read_config(path) -> Config:
    with open(path, "r") as config_json:
        config = json.load(config_json)
    return Config(**config)


CONFIG = read_config("config.json")
DSC_TIME = dt.time.fromisoformat(CONFIG.dsc_poll_time)
DSC_TIME = dt.time.replace(DSC_TIME, tzinfo=ZoneInfo(CONFIG.dsc_tz))


def read_secrets():
    # parse secrets from .env file
    dotenv.load_dotenv()

    # get secrets: while token is str, parse ids to int
    secrets = {
        "TOKEN": os.getenv("TOKEN"),
        "GUILD": int(os.getenv("GUILD")),
        "ATTENDANCE_CHANNEL": int(os.getenv("ATTENDANCE_CHANNEL")),
        "PIZZA_CHANNEL": int(os.getenv("PIZZA_CHANNEL")),
        "APP_ID": int(os.getenv("APP_ID"))
    }

    return secrets


class CakeCog(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.voice_lines = self.read_voice_lines()

    @commands.hybrid_command(name="cake", description="Definitely not a lie!")
    async def cake(self, ctx):
        """Sends a random GladOS voiceline."""
        msg = "The cake is a lie!"
        if self.voice_lines is not None:
            msg = random.choice(self.voice_lines)
        if msg != "":
            await ctx.send(msg)

    def read_voice_lines(self):
        # load glados voice lines
        voice_lines = None

        try:
            with open("portal_glados_lines.json", "r") as f:
                voice_lines = json.load(f)
        except FileNotFoundError:
            logger.warning("Couldn't find voice lines file!")

        return voice_lines


class PizzaPollCog(commands.Cog):
    def __init__(self, bot: discord.Client, channel):
        super().__init__()

        self.bot = bot
        self.channel = channel

        # will choose a random emoji for each poll option from this dict
        self.emojis = {
            "vegan": ["\N{pineapple}", "\N{potato}", "\N{carrot}", "\N{broccoli}", "\N{cactus}"],
            "vegetarian": ["\N{cheese wedge}", "\N{egg}", "\N{baby bottle}"],
            "carnivore": ["\N{bacon}", "\N{hatching chick}", "\N{pig face}"],
            "nothing": ["\N{face with no good gesture}", "\N{cross mark}", "\N{no entry}"]
        }

        self.post_pizza_poll_task.start()

    def cog_unload(self):
        return self.post_pizza_poll_task.cancel()

    @tasks.loop(time=DSC_TIME)
    async def post_pizza_poll_task(self):
        now = dt.datetime.now()
        if dt.datetime.weekday(now) != CONFIG.dsc_poll_weekday:
            return

        logger.info("posting pizza poll")

        duration = dt.timedelta(hours=1)

        pizza_poll = discord.Poll(
            question="Ding dong, here is the Pizza-Pollice from Pizzapolis!",
            multiple=False,
            duration=duration
        )

        pizza_poll.add_answer(text="Vegan", emoji=random.choice(self.emojis["vegan"]))
        pizza_poll.add_answer(text="Vegetarian", emoji=random.choice(self.emojis["vegetarian"]))
        pizza_poll.add_answer(text="Carnivore", emoji=random.choice(self.emojis["carnivore"]))
        pizza_poll.add_answer(text="But I refuse!", emoji=random.choice(self.emojis["nothing"]))

        channel = self.bot.get_channel(self.channel)
        await channel.send(poll=pizza_poll)

    @post_pizza_poll_task.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()


class AttendancePollCog(commands.Cog):
    def __init__(self, bot: discord.Client, channel):
        super().__init__()
        self.bot = bot
        self.channel = channel

        self.post_attendance_poll_task.start()

    def cog_unload(self):
        self.post_attendance_poll_task.cancel()

    @tasks.loop(time=DSC_TIME)
    async def post_attendance_poll_task(self):
        now = dt.datetime.now()
        if dt.datetime.weekday(now) != CONFIG.dsc_poll_weekday:
            return

        logger.info("posting attendance poll")

        duration = dt.timedelta(hours=1)

        attendance_poll = discord.Poll(
            question="Data is calling! Will you attend DSC today?",
            multiple=False,
            duration=duration
        )

        attendance_poll.add_answer(text="Yes", emoji="\N{heavy large circle}")
        attendance_poll.add_answer(text="No", emoji="\N{cross mark}")

        channel = self.bot.get_channel(self.channel)
        await channel.send(poll=attendance_poll)

    @post_attendance_poll_task.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()


class DSCBot(commands.Bot):
    def __init__(self, attendance_channel, pizza_channel, command_prefix="$", **kwargs):
        super().__init__(command_prefix, **kwargs)
        self.attendance_channel = attendance_channel
        self.pizza_channel = pizza_channel

    async def setup_hook(self):
        logger.info("setup hook")

        logger.info("add cake cog")
        cake_cog = CakeCog(self)
        await self.add_cog(cake_cog)

        logger.info("add attendance cog")
        attendance_cog = AttendancePollCog(self, self.attendance_channel)
        await self.add_cog(attendance_cog)

        logger.info("add pizza cog")
        pizza_cog = PizzaPollCog(self, self.pizza_channel)
        await self.add_cog(pizza_cog)

    async def on_ready(self):
        logger.info(f"logged in as {self.user} (ID: {self.user.id})")

        logger.info("sync command tree")
        await self.tree.sync()

        logger.info("ready")


async def main():
    logger.addHandler(logging.StreamHandler())
    logger.addHandler(logging.FileHandler("bot.log"))
    logger.setLevel(logging.INFO)

    intents = discord.Intents.default()

    secrets = read_secrets()

    bot = DSCBot(secrets["ATTENDANCE_CHANNEL"], secrets["PIZZA_CHANNEL"], intents=intents)

    await bot.start(secrets["TOKEN"])

if __name__ == "__main__":
    asyncio.run(main())
