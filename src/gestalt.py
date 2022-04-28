from events import Events
from macros import Macros
from voting import Voting
from miscellenous import Miscellenous
from persistent import *


# Fetches configuration information
comList = []
discordAuthcode = ""
with open(DAC_FILE, "r") as discordAuthfile:
    discordAuthcode = discordAuthfile.read().strip()

# Sets Google's credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GAJ_FILE

# Creates basic bot object
help_overwrite = commands.DefaultHelpCommand(no_category="Help")
intents_overwrite = discord.Intents.default()
intents_overwrite.members = True
intents_overwrite.messages = True
bot = commands.Bot(command_prefix=COM_PRFX, description="Gestalt's Help Menu", help_command=help_overwrite, intents=intents_overwrite)


# Creates a task to iterate randomly through creative messages
@tasks.loop(minutes=random.randint(1,5))
async def random_presence():
    choice = presenceList[random.randint(0, len(presenceList)-1)]
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=choice))

# Creates a task to backup active nomination instances
@tasks.loop(minutes=5)
async def backup_nominations():
    repickles(NBP_FILE, nominationMap)

# DEBUG: Executes on Interval, good for live-testing
#@tasks.loop(seconds=3)
#async def backup_nominations():
#    print(nominationMap)


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

    # Starts backing up nominations list
    backup_nominations.start()


# Adds Cogs to Bot
bot.add_cog(Events(bot))
bot.add_cog(Macros(bot))
bot.add_cog(Voting(bot))
bot.add_cog(Miscellenous(bot))

# Runs Bot
bot.run(discordAuthcode)