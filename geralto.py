import discord
import time
import random
import re
import os
from discord.ext import commands
from datetime import datetime
from persistent import *


################################################################################
# Initializations
################################################################################

# Fetches configuration information
comList = []
discordAuthcode = ""
with open('discordAuth.code', 'r') as discordAuthfile:
    discordAuthcode = discordAuthfile.read().strip()

# Sets Google's credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="Discord Translation Bot-6ea5cf4e9bda.json"
help_overwrite = commands.DefaultHelpCommand(no_category='Commands')
client = commands.Bot(command_prefix=COM_PRFX, description="Gestalt's Help Menu", help_command=help_overwrite)

@client.event
async def on_ready():
    """Initializes the bot's functions.
    """
    # Feedback
    print('{0.user} Version {1} has started.'.format(client, VERSION))
    await client.change_presence(activity=discord.Game("Winds' Howlin'"))

    # Parse Command list
    # cooode


################################################################################
# Commands
################################################################################

#@client.command()
#async def [command name]:
#    """"""
#    print("sample")

# Translate command with directional and language input
@client.command()
async def translate(ctx, direction, destination):
    """Translates from detected language to English, or from detected language to any other. Characters beyond limit are trimmed.

    direction\t- Describes either "to", "into" or "from" as the direction of translation.
    destination\t- Describes the desired language to translate "to", "into" or "from".
    """

    # Tokenizes entry
    tokens = (ctx.message.content).split()
    direction = direction.lower()
    msg = (" ".join(tokens[3:])).replace('&#39;', '')

    # Imposes character limit
    if len(msg) > MAX_MESG:
        await ctx.send("Message is longer than " + str(MAX_MESG) + " characters, trimming to " + str(MAX_MESG) + ".")
        msg = msg[:MAX_MESG]

    # Breaks down by direction and language
    if direction == "into" or direction == "to":
        language_code = language_lookup(destination)
        if language_code is not None:
            await ctx.send(str(translate_text(language_code, msg)).replace('&#39;', ''))
        else:
            await ctx.send("Could not find desired language.")
    elif direction == "from":
        await ctx.send(str(translate_text("en", msg)).replace('&#39;', ''))
    else:
        await ctx.send("Could not recognize desired direction, try \"into\",\"to\" or \"from\" instead.")


# Rolls DnD dice
@client.command()
async def roll(ctx, roll_query):
    """Rolls a DnD dice with support for dropping and rerolling with general format \"~roll [numDice]d[maxRoll]r[rerollFloor]d[numDrop]\"

    roll_query\t- Describes the die.
    """

    # Breaks die down to components following archetype: /roll [numDice]d[maxRoll] with options r[rerollFloor] and d[numDrop]
    # in that order.
    dCapture = re.findall("[-\d]*d[-\d]+", roll_query)
    rCapture = re.findall("r[-\d]*", roll_query)

    # Does cumulative error feedback on initial query
    if len(dCapture) < 1 or len(dCapture) > 2 or len(rCapture) > 1:
        if len(dCapture) < 1:
            await ctx.send("Malformed: Missing primary die of form \"[numDice]d[maxRoll]\".")
        if len(dCapture) > 2:
            await ctx.send("Malformed: Discovered more than two potential occurences of primary or drop die.")    
        if len(rCapture) > 1:
            await ctx.send("Malformed: Discovered more than one potential occurence of reroll die.")
        return

    # Captures number of dice to drop
    numDrop = int(dCapture[1].split('d')[1]) if len(dCapture) == 2 else 0

    # Captures minimum roll value before reroll
    rerollFloor = int(rCapture[0].split("r")[1]) if len(rCapture) == 1 else 1

    # Captures primary roll information
    numDice = dCapture[0].split('d')
    maxRoll = int(numDice[1])
    numDice = int(numDice[0]) if len(numDice[0]) > 0 else 1

    # Notes occurrence order
    dFirst = roll_query.find(dCapture[0])
    dLast = roll_query.rfind(dCapture[-1]) if numDrop > 0 else None
    rFirst = roll_query.find(rCapture[0]) if rerollFloor > 1 else None
    
    # Does checking on ordering
    if (len(dCapture) > 0 and len(rCapture) > 0 and dFirst > rFirst) or (dLast is not None and len(dCapture) > 1 and len(rCapture) > 0 and dLast < rFirst):
        if len(dCapture) > 0 and len(rCapture) > 0 and dFirst > rFirst:
            await ctx.send("Malformed: Missing primary die, check die ordering.")
        if len(dCapture) > 1 and len(rCapture) > 0 and dLast < rFirst:
            await ctx.send("Malformed: Drop die should not preceed rerolls.")
        return

    # Does checking on relative values reasonability
    if rerollFloor > maxRoll or numDrop > numDice or min(numDice, maxRoll, rerollFloor, numDrop) < 0:
        if rerollFloor > maxRoll:
            await ctx.send("Malformed: Minimum desired roll is greater than highest possible.")
        if numDrop > numDice:
            await ctx.send("Malformed: Dropping more lowest die than dice have been rolled.")
        if min(numDice, maxRoll, rerollFloor, numDrop) < 0:
            await ctx.send("Malformed: Negative values are unacceptable.")
        return

    # Debugging Info
    await ctx.send("Got numDice:" + str(numDice) + "\nGot maxRoll:" + str(maxRoll) + 
                "\nGot rerollFloor:" + str(rerollFloor) + "\nGot numDrop:" + str(numDrop) +
                "\nMin of rolls:" + str(min(numDice, maxRoll, rerollFloor, numDrop)))

    # Feedback and breakdown of roll
    await ctx.send("Rolling " + roll_query + "...")

    dieRolls = []
    for i in range(numDice):
        dieRolls.append(random.randint(rerollFloor,maxRoll))

    dieRolls.sort(reverse=True)
    if numDrop > 0:
        del dieRolls[-numDrop:]
    await ctx.send("Got: " + str(dieRolls) + "\nSum: " + str(sum(dieRolls)))


# Bot kill command
@client.command()
async def begone(ctx):
    """Kills the bot script. Please only use if you know what you're doing.
    """

    # Kills the bot
    await ctx.bot.logout()


# Runs bot
client.run(discordAuthcode)
