import discord
import time
from discord.ext import commands
from datetime import datetime
from persistent import *


# Fetches configuration information
comList = []
authCode = ""
with open('auth.code', 'r') as authfile:
    authCode = authfile.read().strip()


# Initializes Bot
client = commands.Bot(command_prefix='!')


@client.event
async def on_ready():
    # Feedback
    print('{0.user} Version {1} has started.'.format(client, VERSION))
    await client.change_presence(activity=discord.Game("Winds' Howlin'"))

    # Parse Command list


# Remind feature
@client.command(pass_context=True)
async def remind(ctx):
    return

# Kick the bot
@client.command(pass_context=True)
async def begone(ctx):
    await ctx.bot.logout()


# Runs bot
client.run(authCode)
