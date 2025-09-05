import asyncio
from discord.ext import commands
import messageSend


class reactionwait(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def reactionwait(self, ctx, message):
        print(f"{ctx.author.name} - reaction wait")
        react = ["✅", "❌"]  # reactions to be added under question "\U00002705", "\U0000274c" "✅", "❌"
        #post embed message with a question
        print(f"{ctx.author.name} - reaction wait - send a question")
        question = await messageSend.postMessage(ctx, message, "Question")
        #add reactions to the message
        print(f"{ctx.author.name} - reaction wait - get reaction")
        for r in react:  # loop add reactions
            await question.add_reaction(r)
        #check reaction to the question
        print(f"{ctx.author.name} - reaction wait - check if {ctx.author.name} reacted")
        def check(reaction, user):
            return user == ctx.author and reaction.emoji in react
        #wait for reaction
        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)

        except asyncio.TimeoutError:
            print(f"{ctx.author.name} - reaction wait - reaction timed out")
            return "timeout"
            #await messageSend.postMessage(ctx, "timeout!!", "Fail")
        #if reaction added, return user intention
        else:
            if str(reaction) == "✅":
                print(f"{ctx.author.name} - reaction wait - reaction PASS")
                return "proceed"
            elif str(reaction) == "❌":
                print(f"{ctx.author.name} - reaction wait - reaction FAIL")
                return "cancel"

async def setup(bot):
    await bot.add_cog(reactionwait(bot))