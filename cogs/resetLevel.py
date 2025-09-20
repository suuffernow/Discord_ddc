import psycopg2,os
from discord import app_commands
from discord.ext import commands
import userExistCheck, messageSend
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

class resetlevel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="resetlevel", brief="Resets level of selected skill")
    @app_commands.choices(skill=[
        app_commands.Choice(name="Attack", value="atk"),
        app_commands.Choice(name="HP", value="hp"),
        app_commands.Choice(name="Dexterity", value="dex"),
        app_commands.Choice(name="Speed", value="spd")])
    async def resetlevel(self, ctx, skill:app_commands.Choice[str]):
        print(f"{ctx.author.name} - reset level")
        # check if user already exist
        print(f"{ctx.author.name} - reset level - check if user exists")
        if userExistCheck.userExist(ctx.author.id) == "found":
            # trigger function to add new user
            print(f"{ctx.author.name} - reset level - user found - try to reset level")
            result = await self.reset(ctx, skill.value)

        else:# user doesnt exist
            print(f"{ctx.author.name} - reset level - user does not exist")
            emoji = "<:annoy:1412540836167684116>"
            result = ["Fail", f"❌ {emoji} your character doesn't exist!"]

        await messageSend.postMessage(ctx, result[1], result[0])


    async def reset(self, ctx, skill):
        print(f"{ctx.author.name} - reset level {skill} - log into database")
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                # get characters statistics
                print(f"{ctx.author.name} - reset level - get user stats")
                skillValue = skill+"_value"
                cur.execute("SELECT exp, {}, {} FROM ddc_player WHERE player_id = {}".format(skill,skillValue,ctx.author.id))
                playerstats = cur.fetchone()
                print(playerstats)
                recoveryEXP = playerstats[0]

                for i in range(playerstats[1]+1):
                    recoveryEXP += i

                emojiwhat = "<:what:1412543722901602304>"
                message = f"❔❓ {emojiwhat} Do you want to {skill} level and recover {recoveryEXP} exp?"

                print(f"{ctx.author.name} - reset level - ask for confirmation")
                from cogs.reactionWait import reactionwait
                ask = reactionwait(bot=self.bot)
                question = await ask.reactionwait(ctx, message)

                if question == "timeout":
                    print(f"{ctx.author.name} - reset level - timeout")
                    emoji = "<:zlowenergy:1412527768540811325>"
                    return "Fail", f"{emoji} timeout!!"

                if question == "cancel":
                    print(f"{ctx.author.name} - reset level - cancelled")
                    emoji = "<:annoy:1412540836167684116>"
                    return "Fail", f"❌ {emoji} level reset canceled!"

                if question == "proceed":
                    print(f"{ctx.author.name} - reset level - confirmed")

                    cur.execute("UPDATE ddc_player SET exp = {}, {} = 0, {} = 2 where player_id = {}".format(recoveryEXP, skill, skillValue, ctx.author.id))
                    emoji = "<:angle:1412540828701823007>"
                    return "Pass", f"✅ {emoji} {skill} level has been reset. {recoveryEXP} exp available to spend."

async def setup(bot):
    await bot.add_cog(resetlevel(bot))