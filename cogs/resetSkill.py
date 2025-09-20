import psycopg2,os
from discord.ext import commands
import userExistCheck, messageSend
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

class resetskill(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="resetskill", brief="Resets all skill levels")
    async def resetskill(self, ctx):
        print(f"{ctx.author.name} - skill reset")
        # check if user already exist
        print(f"{ctx.author.name} - skill reset - check if user exists")
        if userExistCheck.userExist(ctx.author.id) == "found":
            # trigger function to add new user
            print(f"{ctx.author.name} - skill reset - user found - try to level up skill")
            result = await self.reset(ctx)

        else:# user doesnt exist
            print(f"{ctx.author.name} - skill reset - user does not exist")
            emoji = "<:annoy:1412540836167684116>"
            result = ["Fail", f"❌ {emoji} your character doesn't exist!"]

        await messageSend.postMessage(ctx, result[1], result[0])


    async def reset(self, ctx):
        print(f"{ctx.author.name} - skill reset - log into database")
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                # get characters statistics
                print(f"{ctx.author.name} - skill reset - get user stats")
                cur.execute("SELECT * FROM ddc_player WHERE player_id = {}".format(ctx.author.id))
                playerstats = cur.fetchone()
                skillpoints = playerstats[14] + playerstats[15] + playerstats[16] + playerstats[17] + playerstats[18]

                emojiwhat = "<:what:1412543722901602304>"
                message = f"❔❓ {emojiwhat} Do you want to reset skills and recover {skillpoints} skill points?"

                print(f"{ctx.author.name} - skill reset - ask for confirmation")
                from cogs.reactionWait import reactionwait
                ask = reactionwait(bot=self.bot)
                question = await ask.reactionwait(ctx, message)

                if question == "timeout":
                    print(f"{ctx.author.name} - skill reset - timeout")
                    emoji = "<:zlowenergy:1412527768540811325>"
                    return "Fail", f"{emoji} timeout!!"

                if question == "cancel":
                    print(f"{ctx.author.name} - skill reset - cancelled")
                    emoji = "<:annoy:1412540836167684116>"
                    return "Fail", f"❌ {emoji} skill reset canceled!"

                if question == "proceed":
                    print(f"{ctx.author.name} - skill reset - confirmed")

                    cur.execute("UPDATE ddc_player SET skill_points = {}, atk_skill = 0, hp_skill = 0, dex_skill = 0, spd_skill = 0 where player_id = {}".format(skillpoints, ctx.author.id))
                    emoji = "<:angle:1412540828701823007>"
                    return "Pass", f"✅ {emoji} Skill points have been reset. {skillpoints} available to spend"

async def setup(bot):
    await bot.add_cog(resetskill(bot))