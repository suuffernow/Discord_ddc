import psycopg2, os
from discord import app_commands
from discord.ext import commands
import userExistCheck, messageSend
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

class userlevelup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="levelup",brief="levels up mentioned skill by X level")
    @app_commands.choices(skill=[
        app_commands.Choice(name="Attack", value="atk"),
        app_commands.Choice(name="HP", value="hp"),
        app_commands.Choice(name="Dexterity", value="dex"),
        app_commands.Choice(name="Speed", value="spd")])
    async def userlevelUp(self, ctx, skill:app_commands.Choice[str], level=1):
        print(f"{ctx.author.name} - levelup - skill:{skill} ||level:{level}")
        # check if user already exist
        print(f"{ctx.author.name} - levelup - check if user exists")
        if userExistCheck.userExist(ctx.author.id) == "found":
            # trigger function to add new user
            print(f"{ctx.author.name} - levelup - user found - try to level up skill")
            result = await self.levelup(ctx, skill.value, level)

        else:# user doesnt exist
            print(f"{ctx.author.name} - levelup - user does not exist")
            emoji = "<:annoy:1412540836167684116>"
            result = ["Fail", f"❌ {emoji} your character doesn't exist!"]

        await messageSend.postMessage(ctx, result[1], result[0])

    async def levelup(self,ctx,skill,level):
        print(f"{ctx.author.name} - levelup - log into database")
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                # get characters statistics, exp and skill level
                print(f"{ctx.author.name} - levelup - get user stats")
                cur.execute("SELECT {}, {} FROM ddc_player WHERE player_id = {}".format("exp", skill, ctx.author.id))
                playerstats = cur.fetchone()

                # set variables to check if upgrade is possible
                print(f"{ctx.author.name} - levelup - assign user stats to variables")
                upgrade_Cost = 0
                current_exp = playerstats[0]
                current_level = playerstats[1]
                desired_level = playerstats[1] + level

                # get list of upgrades to do
                print(f"{ctx.author.name} - levelup - get list of skill:{skill} levelups to do")
                cur.execute("SELECT {},{} from player_stats where level > {} and level <= {}".format("exp", skill,current_level,desired_level))
                skillList = cur.fetchall()

                # check if all upgrades are possible
                print(f"{ctx.author.name} - levelup - loop through list of skill:{skill} levelups")
                for i in range(1, level + 1):
                    upgrade_Cost += skillList[i - 1][0]
                    print(f"current exp: {current_exp} || upgrade_Cost: {upgrade_Cost}")
                    if current_exp < upgrade_Cost:
                        #if not a single level up is possible
                        print(f"{ctx.author.name} - levelup - skill:{skill} level up not possible")
                        if i-1 == 0:
                            emoji = "<:debil:1412540842660335676>"
                            return "Fail", f"❌ {emoji} Not enough exp to level up {skill}"

                        # ask for confirmation if full upgrade not possible
                        emojiwhat = "<:what:1412543722901602304>"
                        message = f"❔❓ {emojiwhat} Not enough EXP to level up **{skill}** by {level}\n\n {i - 1} level ups are available, would you like to proceed?"

                        print(f"{ctx.author.name} - levelup - skill:{skill} partial level up possible - send question")
                        from cogs.reactionWait import reactionwait
                        ask = reactionwait(bot=self.bot)
                        question = await ask.reactionwait(ctx, message)

                        if question == "proceed":
                            print(f"{ctx.author.name} - levelup - skill:{skill} partial level up confirmed")
                            desired_level = playerstats[1] + i - 1
                            upgrade_Cost -= skillList[i - 1][0]
                            break
                        if question == "cancel":
                            print(f"{ctx.author.name} - levelup - skill:{skill} partial level up cancelled")
                            emoji = "<:annoy:1412540836167684116>"
                            return "Fail", f"❌ {emoji} level up canceled!"
                        if question == "timeout":
                            print(f"{ctx.author.name} - levelup - skill:{skill} timeout")
                            emoji = "<:zlowenergy:1412527768540811325>"
                            return "Fail", f"{emoji} timeout!!"

                print(f"skill: {skill} || desired level: {desired_level} || upgrade_Cost: {upgrade_Cost} || author: {ctx.author.id}")
                if current_exp >= upgrade_Cost:
                    print(f"{ctx.author.name} - levelup - skill:{skill} level up confirmed")
                    print(f"{ctx.author.name} - levelup - skill:{skill} get skill value from database")
                    cur.execute("SELECT {} from player_stats WHERE level = {}".format(skill, desired_level))
                    value = cur.fetchone()[0]
                    print(f"{ctx.author.name} - levelup - skill:{skill} update player sheet")
                    cur.execute("UPDATE ddc_player SET exp = {}, {} = {}, {} = {} WHERE player_id = {}".format(
                        current_exp - upgrade_Cost, skill, desired_level, skill + "_value", value, ctx.author.id))
                    print(f"{ctx.author.name} - levelup - skill:{skill} success - send message")
                    emoji = "<:angle:1412540828701823007>"
                    return "Pass", f"✅ {emoji} {skill} has been leveled up to {desired_level}!\n {current_exp - upgrade_Cost} EXP left"


async def setup(bot):
    await bot.add_cog(userlevelup(bot))