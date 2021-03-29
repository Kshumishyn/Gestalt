import datetime
from macros import Macros
from voting import Voting
from persistent import *
from voting import *
from macros import *
from miscellenous import *


# Fetches configuration information
comList = []
discordAuthcode = ""
with open(DAC_FILE, "r") as discordAuthfile:
    discordAuthcode = discordAuthfile.read().strip()

# Sets Google's credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GAJ_FILE

# Creates basic bot object
help_overwrite = commands.DefaultHelpCommand(no_category="Help")
bot = commands.Bot(command_prefix=COM_PRFX, description="Gestalt's Help Menu", help_command=help_overwrite)


# Creates a task to iterate randomly through creative messages
@tasks.loop(minutes=random.randint(1,5))
async def random_presence():
    choice = presenceList[random.randint(0, len(presenceList)-1)]
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=choice))


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


# Adds Cogs to Bot
bot.add_cog(Voting(bot))
bot.add_cog(Macros(bot))
bot.add_cog(Miscellenous(bot))

# Runs Bot
bot.run(discordAuthcode)