import asyncio
import re
from persistent import *


class Miscellenous(commands.Cog):

    # Initialization
    def __init__(self, bot):
        self.bot = bot
        

    # Translate command with directional and language input
    @commands.command()
    async def translate(self, ctx, direction, destination, *message):
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
    @commands.command()
    async def roll(self, ctx, roll_query):
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
    @commands.command()
    async def remind(self, ctx, target: discord.Member, number, unit, *message):
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

        # Gives feedback
        await ctx.send("Will do " + target.mention + "!")

        # Removes request message for cleanliness
        await ctx.message.delete()

        # Commences wait
        await asyncio.sleep(number * mult)
        await ctx.send(target.mention + " " + message)


    # Bot kill command
    @commands.command()
    async def begone(self, ctx):
        """Kills the bot script. Please only use if you know what you're doing.
        """

        # Removes request message for cleanliness
        await ctx.message.delete()

        # Kills the bot
        await ctx.bot.logout()


# Necessary for Cog Setup
def setup(bot):
    bot.add_cog(Miscellenous(bot))