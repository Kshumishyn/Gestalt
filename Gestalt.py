import discord
import random
import asyncio
import datetime
import re
from discord.ext import commands, tasks
from string import ascii_lowercase
from persistent import *


################################################################################
# Initializations
################################################################################

# Fetches configuration information
comList = []
discordAuthcode = ""
with open(DAC_FILE, "r") as discordAuthfile:
    discordAuthcode = discordAuthfile.read().strip()

# Sets Google's credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GAJ_FILE
help_overwrite = commands.DefaultHelpCommand(no_category="Commands")
bot = commands.Bot(command_prefix=COM_PRFX, description="Gestalt's Help Menu", help_command=help_overwrite)

# Bot Initialization
@bot.event
async def on_ready():
    """Initializes the bot's functions.
    """

    # Feedback
    print("{0.user} Version {1} has started.".format(bot, VERSION))
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="the beginning."))

    # Starts Random Presence
    random_presence.start()


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
async def translate(ctx, direction, destination, *message):
    """Translates from detected language to English, or from detected language to any other. Characters beyond limit are trimmed. Follows general format \"~translate [direction] [destination] [message]\"

    direction\t- Describes either "to", "into" or "from" as the direction of translation.
    destination\t- Describes the desired language to translate "to", "into" or "from".
    message\t- Describes the message to translate.
    """

    # Tokenizes entry
    direction = direction.lower()
    message = " ".join(message).replace("&#39;", "")

    # Imposes character limit
    if len(message) > MAX_MESG:
        await ctx.send("Message is longer than " + str(MAX_MESG) + " characters, trimming to " + str(MAX_MESG) + ".")
        message = message[:MAX_MESG]

    # Breaks down by direction and language
    if direction == "into" or direction == "to":
        language_code = language_lookup(destination)
        if language_code is not None:
            await ctx.send(str(translate_text(language_code, message)).replace("&#39;", ""))
        else:
            await ctx.send("Could not find desired language.")
    elif direction == "from":
        await ctx.send(str(translate_text("en", message)).replace("&#39;", ""))
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
    numDrop = int(dCapture[1].split("d")[1]) if len(dCapture) == 2 else 0

    # Captures minimum roll value before reroll
    rerollFloor = int(rCapture[0].split("r")[1]) if len(rCapture) == 1 else 1

    # Captures primary roll information
    numDice = dCapture[0].split("d")
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

    # Accumulates rolls
    dieRolls = []
    for i in range(numDice):
        dieRolls.append(random.randint(rerollFloor,maxRoll))

    # Trims lowest rolls
    dieRolls.sort(reverse=True)
    if numDrop > 0:
        del dieRolls[-numDrop:]

    # Provides roll feedback
    await ctx.send("Rolling " + roll_query + "...\nGot: " + str(dieRolls) + "\nSum: " + str(sum(dieRolls)))


# Remind a specific user with a message
@bot.command()
async def remind(ctx, target: discord.Member, number, unit, *message):
    """Creates an Asynchronous Reminder with general format \"~remind [target] [number] [unit] [message]\"

    target\t- Describes the person to remind.
    number\t- Describes the quantitative duration.
    unit\t- Describes the unit of time.
    message\t- The remainder of the command is sent upon Reminder's expiration.
    """

    # Does error checking on number
    if not isnumber(number):
        await ctx.send("Malformed: Quantity provided is not a number (NaN).")
        return
    number = int(float(number))

    # Does error checking on units
    unit = unit.lower()
    if unit in timeMap:
        mult = timeMap[unit]
    else:
        await ctx.send("Malformed: Nonstandard unit provided. Example: \"mins\" or \"minutes\".")
        return

    # Formats message
    message = (" ".join(message)).replace("&#39;", "")

    # Commences wait
    await asyncio.sleep(number * mult)
    await ctx.send(target.mention + " " + message)


# Creates a Nomination Instance
@bot.command()
async def begin_noms(ctx, inst_name):
    """Attempts to start a nomination instance with a given name.

    inst_name\t- The desired name of instance to add.
    """

    # Creates a tuple unique to the server
    guildID = ctx.message.guild.id
    unique_inst = (guildID, inst_name.lower())

    # Checks if nomination instance already exists on this server
    if unique_inst in nominationMap:
        await ctx.send("Nomination Instance: " + str(inst_name) + " already in the nominations, try again.")
        return

    # Adds the instance of nomination
    nominationMap[unique_inst] = {}
    await ctx.send("**__Starting Nominations__**\nUse \"" + str(inst_name) + "\" as the code to access this poll. Example:\n`~nom_add " + str(inst_name) + " Who Killed Captain Alex`")


# Ends a Nomination Instance
@bot.command()
async def cancel_noms(ctx, inst_name):
    """Attempts to remove a nomination instance with a given name.

    inst_name\t- The desired name of nomination instance to remove.
    """

    # Creates a tuple unique to the server
    guildID = ctx.message.guild.id
    unique_inst = (guildID, inst_name.lower())

    # Checks if nomination instance exists on this server
    if unique_inst not in nominationMap:
        await ctx.send("Nomination Instance: " + str(inst_name) + " cannot be removed because it does not exist, try again.")
        return

    # Removes nomination instance
    del nominationMap[unique_inst]
    await ctx.send("Cancelled Nominations instance for " + str(inst_name) + ".")


# Add a nomination
@bot.command()
async def nom_add(ctx, inst_name, *nom):
    """Attempts to add a nomination to an existing nomination instance. Displays nomination list for 20 seconds after valid input.

    inst_name\t- The desired name of nomination instance to add to.
    nom\t\t- The desired nomination
    """

    # Creates a tuple unique to the server
    guildID = ctx.message.guild.id
    unique_inst = (guildID, inst_name.lower())

    # Checks if nomination instance exists on this server
    if unique_inst not in nominationMap:
        await ctx.send("Nomination Instance: " + str(inst_name) + " does not exist, try again.")
        return

    # Adds nomination to the instance
    userID = ctx.author.id
    nominationMap[unique_inst][userID] = " ".join(nom)

    # Creates list of current nominations
    await ctx.send("**__Nominations for " + str(inst_name) + ":__**\n" + "\n".join(str(nominationMap[unique_inst][key]) for key in sorted(nominationMap[unique_inst])), delete_after=20)

    # Removes request message for anonymity
    await ctx.message.delete()


# Removes a nomination
@bot.command()
async def nom_remove(ctx, inst_name):
    """Attempts to remove a nomination from an existing nomination instance. Displays nomination list for 20 seconds after valid input.

    inst_name\t- The desired name of nomination instance to remove from.
    """

    # Creates a tuple unique to the server
    guildID = ctx.message.guild.id
    unique_inst = (guildID, inst_name.lower())

    # Checks if nomination instance exists on this server
    if unique_inst not in nominationMap:
        await ctx.send("Nomination Instance: " + str(inst_name) + " does not exist, try again.")
        return

    # Removes nomination from the instance
    userID = ctx.author.id
    nominationMap[unique_inst].pop(userID, None)

    # Creates list of current nominations
    await ctx.send("**__Nominations for " + str(inst_name) + ":__**\n" + "\n".join(str(nominationMap[unique_inst][key]) for key in sorted(nominationMap[unique_inst])), delete_after=20)

    # Removes request message for anonymity
    await ctx.message.delete()


# Lists all active nominations
@bot.command()
async def nom_list(ctx, inst_name):
    """Attempts to list nominations for an existing nomination instance.

    inst_name\t- The desired name of nomination instance whose nominations to list.
    """

    # Creates a tuple unique to the server
    guildID = ctx.message.guild.id
    unique_inst = (guildID, inst_name.lower())

    # Checks if nomination instance exists on this server
    if unique_inst not in nominationMap:
        await ctx.send("Nomination Instance: " + str(inst_name) + " does not exist, try again.")
        return

    # Creates list of current nominations
    await ctx.send("**__Nominations for " + str(inst_name) + ":__**\n" + "\n".join(str(nominationMap[unique_inst][key]) for key in sorted(nominationMap[unique_inst])))

    # Removes request message for cleanliness
    await ctx.message.delete()


# Transfers Nomination Instance into a Voting Instance
@bot.command()
async def begin_voting(ctx, inst_name, *message):
    """Attempts to start a voting instance using the already built nomination instance.

    inst_name\t- The desired name of nomination instance whose nominations to create votes for.
    message\t- An optional message to attach with the start of voting.
    """

    # Processes
    message = " ".join(message)

    # Creates a tuple unique to the server
    guildID = ctx.message.guild.id
    unique_inst = (guildID, inst_name.lower())

    # Checks if nomination instance exists on this server
    if unique_inst not in nominationMap:
        await ctx.send("Nomination Instance: " + str(inst_name) + " does not exist, try again.")
        return

    # Checks if nomination instance has been developed
    if len(nominationMap[unique_inst]) == 0:
        await ctx.send("Nomination Instance: " + str(inst_name) + " is empty, try again.")
        return

    # Prepares Table
    table = ""
    letter_iter = 0
    for key in sorted(nominationMap[unique_inst]):
        table = table + ":" + "regional_indicator_" + ascii_lowercase[letter_iter] + ": : " + str(nominationMap[unique_inst][key]) + "\n"
        letter_iter = letter_iter + 1

    # Sends formatted voting table
    ownMessage = await ctx.send("**__Starting Voting for \"" + str(inst_name) + "\"__**" + ("\n" + message if len(message) > 0 else "") + "\n\n" + table + "\n")

    # Adds reactions to own message
    for i in range(0,letter_iter):
        emote = regional_indicators[ascii_lowercase[i]]
        await ownMessage.add_reaction(emote)

    # Clears nomination from list
    nominationMap.pop(unique_inst, None)
    

# Creates a Macro
@bot.command()
async def macro_set(ctx, macro, *message):
    """Attempts to create a Macro mapping to a message.

    macro\t- Describes the desired macro to create.
    message\t- Describes the message to map to.
    """

    # Processes
    macro = str(macro)
    message = " ".join(message).replace("\\n", "\n")

    # Validates Macro
    if macro in macroMap:
        await ctx.send("Macro: " + macro + " already in the macro mapping, try again.")
        return

    # Adds to Macro Map
    macroMap[macro] = message
    with open(MDJ_FILE, "w") as json_file:
            json.dump(macroMap, json_file)


# Lists existing macros
@bot.command()
async def macro_list(ctx):
    """Iterates through macroMap and lists the Macros
    """

    # Fetches macro list
    await ctx.send("Macro List:\n\n" + "\n".join([str(k + ":\n\"" + " ".join(v.split(" ")[:min(len(v), MAX_PRVW)]) + "\"\n") for k,v in macroMap.items()]))


# Uses a macro
@bot.command()
async def macro(ctx, macro):
    """Attempts to use an existing Macro.

    macro\t- Describes the desired macro to lookup.
    """

    # Processes
    macro = str(macro)

    # Validates Macro
    if macro not in macroMap:
        await ctx.send("Macro: " + macro + " was not in the macro mapping, try again.")
        return

    # Uses macro
    await ctx.send(macroMap[macro])

    # Removes request message for cleanliness
    await ctx.message.delete()


# Removes a macro
@bot.command()
async def macro_remove(ctx, macro):
    """Attempts to remove an existing Macro.

    macro\t- Describes the desired macro to lookup.
    """

    # Processes
    macro = str(macro)

    # Validates Macro
    if macro not in macroMap:
        await ctx.send("Macro: " + macro + " was not in the macro mapping, try again.")
        return

    # Removes macro
    macroMap.pop(macro)
    with open(MDJ_FILE, "w") as json_file:
        json.dump(macroMap, json_file)
    await ctx.send("Successfully removed macro: " + macro)


# Handles unrecognized commands
@bot.event
async def on_command_error(ctx, error):
    """Handles broad scope errors.

    error\t- The specific error type.
    """

    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Malformed: Command not found, seek ~help.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Malformed: Sought member was not found in active server.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("Malformed: Missing permissions to perform deletion.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Malformed: Command is missing arguments, type \"~help [command]\" to see syntax.")
    else:
        await ctx.send("Malformed: Unhandled Error. Writing to file.")
        with open(ERR_FILE, "a+") as error_file:
            error_file.write(str(datetime.datetime.now()) + ":\n" + str(error) + "\n\n")
        raise error


# Bot kill command
@bot.command()
async def begone(ctx):
    """Kills the bot script. Please only use if you know what you're doing.
    """

    # Removes request message for cleanliness
    await ctx.message.delete()

    # Kills the bot
    await ctx.bot.logout()


# Runs bot
bot.run(discordAuthcode)