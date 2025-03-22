#!/usr/bin/env python3

import discord
from discord.ext import commands

import os
import sys
from dotenv import load_dotenv

from dungeondice.discord import commandgroups


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)


@bot.event
async def on_ready():
    if bot.user:
        print(f'Logged in as {bot.user} (ID: {bot.user.id})')
        print('------')
    else:
        print('Something is seriously wrong with this bot.')

    await bot.add_cog(commandgroups.Roll())
    await bot.tree.sync()


def start_bot():
    if TOKEN:
        bot.run(TOKEN)
    else:
        sys.exit("Missing a discord token. Supply it as environment variable.")
