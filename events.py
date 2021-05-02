import datetime
from persistent import *


class Events(commands.Cog):

    # Initialization
    def __init__(self, bot):
        self.bot = bot


    # Identifies listener as ready
    async def on_ready(self):
        print("Listener is ready")


    # Handles unrecognized commands
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
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


    # Handles unrecognized commands
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, ctx):
        """Attempts to listen for reactions specifically to voting instances.
        """

        if ctx.message_id == 590509269603057686:
            channel = ctx.get_channel(ctx.channel_id)
            message = await channel.fetch_message(ctx.message_id)
            user = ctx.get_user(ctx.user_id)
            emoji = ctx.get_emoji(577578847080546304)
            await message.remove_reaction(emoji, user)


# Necessary for Cog Setup
def setup(bot):
    bot.add_cog(Events(bot))