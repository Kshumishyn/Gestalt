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

        # Voting instance - Format: {messageID : ({emote : nomination}, max_votes, {userID : (numVotes, [m0...mNV])})}
        # Only handle non-self generated reactions from voting list       
        if not payload.user_id == self.bot.user.id:
            if payload.message_id in votingMap:

                # Processes emote
                emoteMap, maxVotes, userVotes = votingMap[payload.message_id]
                emote = str(payload.emoji)

                # Processes user
                user = self.bot.get_user(payload.user_id)
                
                # Processes removing reaction
                channel = self.bot.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                await message.remove_reaction(emote, user)

                # Validates if relevant emote
                if emote not in emoteMap:
                    return

                # Validates if user exists already
                userRaw = None
                if payload.user_id in userVotes:
                    userRaw = userVotes[payload.user_id]
                else:
                    userRaw = (0, [None for i in range(maxVotes + 1)])

                # Fetches movie and user information
                movie = emoteMap[emote]
                userNumVotes = userRaw[0]
                userMovies = userRaw[1]

                # Validates if movie already exists in user's list
                if movie in userMovies:
                    return

                # Restructures user's movie choices
                userMovies[userNumVotes % maxVotes] = movie
                userNumVotes = userNumVotes + 1

                # Modifies changes into overarching structure
                userMod = (userNumVotes, userMovies)
                userVotes[payload.user_id] = userMod
                votingMap[payload.message_id] = (emoteMap, maxVotes, userVotes)


# Necessary for Cog Setup
def setup(bot):
    bot.add_cog(Events(bot))