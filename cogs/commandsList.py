from discord.ext import commands
import messageSend


class commandslist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="commandslist", description="List available commands")
    async def create(self,ctx):
        try:
            with open("CommandsList.txt", mode="r", encoding="utf-8") as file:
                text = file.read()
        except(Exception) as error:
            print(error)

        await messageSend.postMessage(ctx, text, "Info")

async def setup(bot):
    await bot.add_cog(commandslist(bot))