import discord
import random
import asyncio
import re
import os
from discord.ext import commands, tasks
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
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="googleAuthcode.json"
help_overwrite = commands.DefaultHelpCommand(no_category='Commands')
bot = commands.Bot(command_prefix=COM_PRFX, description="Gestalt's Help Menu", help_command=help_overwrite)

# Bot Initialization
@bot.event
async def on_ready():
    """Initializes the bot's functions.
    """

    # Feedback
    print('{0.user} Version {1} has started.'.format(bot, VERSION))
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="the beginning."))

    # Starts Random Presence
    random_presence.start()

    # Parse Command list
    # cooode


################################################################################
# Tasks
################################################################################

@tasks.loop(minutes=random.randint(1,5))
async def random_presence():
    choice = presenceList[random.randint(0, len(presenceList)-1)]
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=choice))


################################################################################
# Commands
################################################################################

# Translate command with directional and language input
@bot.command()
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
@bot.command()
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

    # Feedback and breakdown of roll
    await ctx.send("Rolling " + roll_query + "...")

    dieRolls = []
    for i in range(numDice):
        dieRolls.append(random.randint(rerollFloor,maxRoll))

    dieRolls.sort(reverse=True)
    if numDrop > 0:
        del dieRolls[-numDrop:]
    await ctx.send("Got: " + str(dieRolls) + "\nSum: " + str(sum(dieRolls)))


# Reminds
@bot.command()
async def remind(ctx, target: discord.Member, number, unit):
    """Creates an Asynchronous Reminder with general format \"~remind [target] [number] [unit] [message]\"

    target\t- Describes the person to remind.
    number\t- Describes the quantitative duration.
    unit\t- Describes the unit of time.
    message\t- The remainder of the command is sent upon Reminder's expiration.
    """

    # Does error checking on number
    if not is_number(number):
        await ctx.send("Malformed: Quantity provided is not a number (NaN).")
        return
    number = int(number)

    # Does error checking on units
    unit = unit.lower()
    if unit in timeMap:
        mult = timeMap[unit]
    else:
        await ctx.send("Malformed: Nonstandard unit provided. Example: \"mins\" or \"minutes\".")
        return

    # Gets Reminder
    tokens = (ctx.message.content).split()
    count = len(target.display_name.split(" "))
    msg = (" ".join(tokens[3 + count:])).replace('&#39;', '')

    # Commences wait
    await asyncio.sleep(number * mult)
    await ctx.send(target.mention + " " + msg)


# Handles unrecognized commands
@bot.event
async def on_command_error(ctx, error):
    """Handles broad scope errors.
    """
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Malformed: Command not found, seek ~help.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Malformed: Sought member was not found in active server.")
    else:
        await ctx.send("Malformed: Unhandled Error.")
        raise error


# Bot kill command
@bot.command()
async def begone(ctx):
    """Kills the bot script. Please only use if you know what you're doing.
    """

    # Kills the bot
    await ctx.bot.logout()


# Runs bot
bot.run(discordAuthcode)