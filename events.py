import datetime
from persistent import *


class Events(commands.Cog):

    # Initialization
    def __init__(self, bot):
        self.bot = bot


    # Handles unrecognized commands
    @commands.Cog.listener()
    async def on_command_error(self, payload, error):
        """Handles broad scope errors.

        error\t- The specific error type.
        """

        if isinstance(error, commands.CommandNotFound):
            await payload.send("Malformed: Command not found, seek ~help.")
        elif isinstance(error, commands.MemberNotFound):
            await payload.send("Malformed: Sought member was not found in active server.")
        elif isinstance(error, commands.MissingPermissions):
            await payload.send("Malformed: Missing permissions to perform deletion.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await payload.send("Malformed: Command is missing arguments, type \"~help [command]\" to see syntax.")
        else:
            await payload.send("Malformed: Unhandled Error. Writing to file.")
            with open(ERR_FILE, "a+") as error_file:
                error_file.write(str(datetime.datetime.now()) + ":\n" + str(error) + "\n\n")
            raise error


    # Handles unrecognized commands
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Attempts to listen for reactions specifically to voting instances.
        """

        # Only handle non-self generated reactions from voting list        
        if not payload.user_id == self.bot.user.id:
            if payload.message_id in votingMap:
                print("Special message!!")
                user = payload.get_user(payload.user_id)
                emoji = payload.get_emoji(577578847080546304)
                await message.remove_reaction(emoji, user)
                '''channel = payload.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                user = payload.get_user(payload.user_id)
                emoji = payload.get_emoji(577578847080546304)
                await message.remove_reaction(emoji, user)'''
            else:
                print("Boring message..")
        else:
            print("Bot message..")


# Necessary for Cog Setup
def setup(bot):
    bot.add_cog(Events(bot))