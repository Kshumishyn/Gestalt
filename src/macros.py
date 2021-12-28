from persistent import *


class Macros(commands.Cog):

    # Initialization
    def __init__(self, bot):
        self.bot = bot
        

    # Creates a Macro
    @commands.command()
    async def macro_set(self, ctx, macro, *, message=None):
        """Attempts to create a Macro mapping to a message.

        macro\t- Describes the desired macro to create.
        message\t- Describes the message to map to.
        """

        # Checks if Macro Message is None and gives feedback
        if not message:
            await ctx.send("Macro message is missing.", delete_after=ERR_TOUT)
            return

        # Cleans up message
        macro = str(macro)
        message = message.replace("\\n", "\n")
        message = message.replace("'", "’")
        message = message.replace("`", "’")

        # Validates Macro
        if macro in macroMap:
            await ctx.send("Macro: " + macro + " already in the macro mapping, try again.", delete_after=ERR_TOUT)
            return

        # Adds to Macro Map
        macroMap[macro] = message
        with open(MDJ_FILE, "w") as json_file:
                json.dump(macroMap, json_file)

        # Removes request message for cleanliness
        await ctx.message.delete()


    # Lists existing macros
    @commands.command()
    async def macro_list(self, ctx):
        """Iterates through macroMap and lists the Macros
        """

        # Fetches macro list
        await ctx.send("Macro List:\n\n" + "\n".join([str(k + ":\n\"" + " ".join(v.split(" ")[:min(len(v), MAX_PRVW)]) + "\"\n") for k,v in macroMap.items()]))

        # TODO: Make it remove previous message instances

        # Removes request message for cleanliness
        await ctx.message.delete()


    # Uses a macro
    @commands.command()
    async def macro(self, ctx, macro):
        """Attempts to use an existing Macro.

        macro\t- Describes the desired macro to lookup.
        """

        # Processes
        macro = str(macro)

        # Validates Macro
        if macro not in macroMap:
            await ctx.send("Macro: " + macro + " was not in the macro mapping, try again.", delete_after=ERR_TOUT)
            return

        # Uses macro
        await ctx.send(macroMap[macro])

        # Removes request message for cleanliness
        await ctx.message.delete()


    # Removes a macro
    @commands.command()
    async def macro_remove(self, ctx, macro):
        """Attempts to remove an existing Macro.

        macro\t- Describes the desired macro to lookup.
        """

        # Processes
        macro = str(macro)

        # Validates Macro
        if macro not in macroMap:
            await ctx.send("Macro: " + macro + " was not in the macro mapping, try again.", delete_after=ERR_TOUT)
            return

        # Removes macro
        macroMap.pop(macro)
        with open(MDJ_FILE, "w") as json_file:
            json.dump(macroMap, json_file)
        await ctx.send("Successfully removed macro: " + macro)

        # Removes request message for cleanliness
        await ctx.message.delete()


# Necessary for Cog Setup
def setup(bot):
    bot.add_cog(Macros(bot))