from persistent import *
from string import ascii_lowercase


class Voting(commands.Cog):

    # Initialization
    def __init__(self, bot):
        self.bot = bot


    # Creates a Nomination Instance
    @commands.command()
    async def begin_noms(self, ctx, inst_name):
        """Attempts to start a nomination instance with a given name.

        inst_name\t- The desired name of instance to add.
        """

        # Creates a tuple unique to the server
        guildID = ctx.message.guild.id
        unique_inst = (guildID, inst_name.lower())

        # Checks if nomination instance already exists on this server
        if unique_inst in nominationMap:
            await ctx.send("Nomination Instance: \"" + str(inst_name) + "\" already in the nominations, try again.", delete_after=NOM_TOUT)
            return

        # Adds the instance of nomination
        nominationMap[unique_inst] = {}
        await ctx.send("**__Starting Nominations__**\nUse \"" + str(inst_name) + "\" as the code to access this poll.\nExample:\n`~nom_add " + str(inst_name) + " Who Killed Captain Alex`")

        # Removes request message for cleanliness
        await ctx.message.delete()


    # Ends a Nomination Instance
    @commands.command()
    async def cancel_noms(self, ctx, inst_name):
        """Attempts to remove a nomination instance with a given name.

        inst_name\t- The desired name of nomination instance to remove.
        """

        # Creates a tuple unique to the server
        guildID = ctx.message.guild.id
        unique_inst = (guildID, inst_name.lower())

        # Checks if nomination instance exists on this server
        if unique_inst not in nominationMap:
            await ctx.send("Nomination Instance: \"" + str(inst_name) + "\" cannot be removed because it does not exist, try again.", delete_after=NOM_TOUT)
            return

        # Removes nomination instance
        del nominationMap[unique_inst]
        await ctx.send("Cancelled Nominations instance for " + str(inst_name) + ".")

        # Removes request message for cleanliness
        await ctx.message.delete()


    # Gives generation instructions on how to add a nomination
    @commands.command()
    async def nom_help(self, ctx):
        """Describes arbitrarily how to nominate something.
        """

        await ctx.send("**__How to nominate__**\nUse a poll code with \"nom_add\" or \"nom_remove\" to add or remove a nomination. Using \"nom_add\" multiple times overwrites previous entries.\nExample:\n`~nom_add [POLL_CODE] Who Killed Captain Alex`")

        # Removes request message for cleanliness
        await ctx.message.delete()


    # Add a nomination
    @commands.command()
    async def nom_add(self, ctx, inst_name, *nom):
        """Attempts to add a nomination to an existing nomination instance. Displays nomination list for 20 seconds after valid input.

        inst_name\t- The desired name of nomination instance to add to.
        nom\t\t- The desired nomination
        """

        # Creates a tuple unique to the server
        guildID = ctx.message.guild.id
        unique_inst = (guildID, inst_name.lower())

        # Checks if nomination instance exists on this server
        if unique_inst not in nominationMap:
            await ctx.send("Nomination Instance: \"" + str(inst_name) + "\" does not exist, try again.", delete_after=NOM_TOUT)
            return

        # Adds nomination to the instance
        userID = ctx.author.id
        nominationMap[unique_inst][userID] = " ".join(nom)

        # Creates list of current nominations
        ownMessage = await ctx.send("**__Nominations for \"" + str(inst_name) + "\":__**\n\n" + "\n".join(str(nominationMap[unique_inst][key]) for key in sorted(nominationMap[unique_inst])))

        # Handles cleaning of 'nom_list' displays
        if unique_inst in nomlistMap:
            messageToDelete = await ctx.fetch_message(nomlistMap[unique_inst])
            await messageToDelete.delete()
        nomlistMap[unique_inst] = ownMessage.id

        # Removes request message for anonymity
        await ctx.message.delete()


    # Removes a nomination
    @commands.command()
    async def nom_remove(self, ctx, inst_name):
        """Attempts to remove a nomination from an existing nomination instance. Displays nomination list for 20 seconds after valid input.

        inst_name\t- The desired name of nomination instance to remove from.
        """

        # Creates a tuple unique to the server
        guildID = ctx.message.guild.id
        unique_inst = (guildID, inst_name.lower())

        # Checks if nomination instance exists on this server
        if unique_inst not in nominationMap:
            await ctx.send("Nomination Instance: \"" + str(inst_name) + "\" does not exist, try again.", delete_after=NOM_TOUT)
            return

        # Removes nomination from the instance
        userID = ctx.author.id
        nominationMap[unique_inst].pop(userID, None)

        # Creates list of current nominations
        ownMessage = await ctx.send("**__Nominations for \"" + str(inst_name) + "\":__**\n\n" + "\n".join(str(nominationMap[unique_inst][key]) for key in sorted(nominationMap[unique_inst])))

        # Handles cleaning of 'nom_list' displays
        if unique_inst in nomlistMap:
            messageToDelete = await ctx.fetch_message(nomlistMap[unique_inst])
            await messageToDelete.delete()
        nomlistMap[unique_inst] = ownMessage.id

        # Removes request message for anonymity
        await ctx.message.delete()


    # Lists all active nominations
    @commands.command()
    async def nom_list(self, ctx, inst_name):
        """Attempts to list nominations for an existing nomination instance.

        inst_name\t- The desired name of nomination instance whose nominations to list.
        """

        # Creates a tuple unique to the server
        guildID = ctx.message.guild.id
        unique_inst = (guildID, inst_name.lower())

        # Checks if nomination instance exists on this server
        if unique_inst not in nominationMap:
            await ctx.send("Nomination Instance: \"" + str(inst_name) + "\" does not exist, try again.", delete_after=NOM_TOUT)
            return

        # Creates list of current nominations
        ownMessage = await ctx.send("**__Nominations for \"" + str(inst_name) + "\":__**\n\n" + "\n".join(str(nominationMap[unique_inst][key]) for key in sorted(nominationMap[unique_inst])))

        # Handles cleaning of 'nom_list' displays
        if unique_inst in nomlistMap:
            messageToDelete = await ctx.fetch_message(nomlistMap[unique_inst])
            await messageToDelete.delete()
        nomlistMap[unique_inst] = ownMessage.id

        # Removes request message for cleanliness
        await ctx.message.delete()


    # Transfers Nomination Instance into a Voting Instance
    @commands.command()
    async def begin_voting(self, ctx, inst_name, max_votes, *message):
        """Attempts to start a voting instance using the already built nomination instance.

        inst_name\t- The desired name of nomination instance whose nominations to create votes for.
        max_votes\t- The number of votes available to each person.
        message\t\t- An optional message to attach with the start of voting.
        """

        # Creates a tuple unique to the server
        guildID = ctx.message.guild.id
        unique_inst = (guildID, inst_name.lower())

        # Processes
        message = " ".join(message)

        # Checks if nomination instance exists on this server
        if unique_inst not in nominationMap:
            await ctx.send("Nomination Instance: \"" + str(inst_name) + "\" does not exist, try again.", delete_after=NOM_TOUT)
            return

        # Checks if nomination instance has been developed
        if len(nominationMap[unique_inst]) == 0:
            await ctx.send("Nomination Instance: \"" + str(inst_name) + "\" is empty, try again.", delete_after=NOM_TOUT)
            return

        # Does error checking on number
        if not isnumber(max_votes):
            await ctx.send("Malformed: Quantity provided is not a number (NaN).", delete_after=NOM_TOUT)
            return
        max_votes = int(float(max_votes))

        # Checks if number of votes is a valid number, notably greater than 0
        if max_votes < 1:
            await ctx.send("Nomination Instance: \"" + str(inst_name) + "\" cannot allow a max of \"" + str(max_votes) + "\" votes.", delete_after=NOM_TOUT)
            return

        # Prepares Table
        table = ""
        voteAsciiMap = {}
        letter_iter = 0
        for key in sorted(nominationMap[unique_inst]):
            letter = ascii_lowercase[letter_iter]
            table = table + ":regional_indicator_" + letter + ": : " + str(nominationMap[unique_inst][key]) + "\n"
            letter_iter = letter_iter + 1
            voteAsciiMap[regional_indicators[letter]] = nominationMap[unique_inst][key]
            
        # Sends formatted voting table
        ownMessage = await ctx.send("**__Starting Voting for \"" + str(inst_name) + "\"__**" + ("\n" + message if len(message) > 0 else "") + "\n\nYou may vote as much as you want but only the most recent " + str(max_votes) + " votes will count.\n" + table + "-------------------------")

        # Adds reactions to own message
        for i in range(0, letter_iter):
            emote = regional_indicators[ascii_lowercase[i]]
            await ownMessage.add_reaction(emote)

        # Prepares Map for reaction reading
        votingMap[ownMessage.id] = (voteAsciiMap, max_votes, {ctx.author.id : (0, [None for i in range(max_votes)])})
        messageMap[inst_name] = ownMessage.id

        # Handles cleaning of 'nom_list' displays
        if unique_inst in nomlistMap:
            messageToDelete = await ctx.fetch_message(nomlistMap[unique_inst])
            await messageToDelete.delete()

        # Removes request message for cleanliness
        await ctx.message.delete()


    # Tallies the total votes and prints a result
    @commands.command()
    async def end_voting(self, ctx, inst_name):
        """Attempts to end a voting instance using the already built nomination instance.

        inst_name\t- The desired name of nomination instance whose nominations to create votes for.
        """

        # Creates a tuple unique to the server
        guildID = ctx.message.guild.id
        unique_inst = (guildID, inst_name.lower())

        # Checks if nomination instance exists on this server
        if unique_inst not in nominationMap:
            await ctx.send("Nomination Instance: \"" + str(inst_name) + "\" does not exist, try again.", delete_after=NOM_TOUT)
            return

        # Determines winner
        userVoteMap = votingMap[messageMap[inst_name]][2]
        movieVoteList = []
        for user in userVoteMap:
            movieVoteList += userVoteMap[user][1]
        voteCount = dict(Counter(movieVoteList))

        # Handles cleaning of 'nom_list' displays
        messageToDelete = await ctx.fetch_message(messageMap[inst_name])
        await messageToDelete.delete()

        # Cleans up all remaining data prematurely
        nominationMap.pop(unique_inst, None)
        votingMap.pop(messageMap[inst_name], None)
        messageMap.pop(inst_name, None)
            
        # Sends formatted voting table
        table = ""
        for movie, votes in voteCount.items():
            if movie is not None and votes is not None:
                table = table + str(votes) + "\t: " + movie + "\n"
        if table == "":
            table = "No votes were cast\n"
        await ctx.send("**__Voting Results for \"" + str(inst_name) + "\":__**\n\n```" + table + "```")

        # Removes request message for cleanliness
        await ctx.message.delete()


# Necessary for Cog Setup
def setup(bot):
    bot.add_cog(Voting(bot))
