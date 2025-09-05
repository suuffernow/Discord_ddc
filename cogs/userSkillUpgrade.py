import psycopg2
from discord import app_commands
from discord.ext import commands
import userExistCheck, messageSend

class userskillup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="skillup",brief="upgrade skill up mentioned skill by X level")
    @app_commands.choices(skill=[
        app_commands.Choice(name="Attack", value="atk"),
        app_commands.Choice(name="HP", value="hp"),
        app_commands.Choice(name="Dexterity", value="dex"),
        app_commands.Choice(name="Speed", value="spd")])
    async def userskillup(self, ctx, skill:app_commands.Choice[str], level=1):
        print(f"{ctx.author.name} - skillup - skill:{skill} ||level:{level}")
        # check if user already exist
        print(f"{ctx.author.name} - skillup - check if user exists")
        if userExistCheck.userExist(ctx.author.id) == "found":
            # trigger function to add new user
            print(f"{ctx.author.name} - skillup - user found - try to level up skill")
            result = await self.skillup(ctx, skill.value, level)

        else:# user doesnt exist
            print(f"{ctx.author.name} - skillup - user does not exist")
            emoji = "<:annoy:1412540836167684116>"
            result = ["Fail", f"❌ {emoji} your character doesn't exist!"]

        await messageSend.postMessage(ctx, result[1], result[0])

    async def skillup(self, ctx, skill, level):
        print(f"{ctx.author.name} - skillup - log into database")
        with psycopg2.connect(dbname="Discord_DDC", user="postgres", password="1234") as conn:
            with conn.cursor() as cur:
                # get characters statistics, exp and skill level
                print(f"{ctx.author.name} - skillup - get user stats")
                cur.execute("SELECT {}, {} FROM ddc_player WHERE player_id = {}".format("skill_points",skill + "_skill",ctx.author.id))
                result = cur.fetchone()

                # set variables to check if upgrade is possible
                print(f"{ctx.author.name} - skillup - assign user stats to variables")
                upgrade_Cost = 0
                skill_points = result[0]
                desired_level = result[1] + level

                # check if all upgrades are possible
                print(f"{ctx.author.name} - skillup - loop through list of skill:{skill} levelups")
                for i in range(1, level + 1):
                    upgrade_Cost += 1
                    if skill_points < i:
                        print(f"{ctx.author.name} - skillup - skill:{skill} level up not possible")
                        if i - 1 == 0:
                            emoji = "<:debil:1412540842660335676>"
                            return "Fail", f"❌ {emoji} Not enough exp to level up {skill}"

                        # ask for confirmation if full upgrade not possible
                        emojiwhat = "<:what:1412543722901602304>"
                        message = f"❔❓ {emojiwhat} Not skill points to upgrade {skill} by {level}\n {i - 1} upgrades ares available, would you like to proceed?"

                        print(f"{ctx.author.name} - skillup - skill:{skill} partial level up possible - send question")
                        from cogs.reactionWait import reactionwait
                        ask = reactionwait(bot=self.bot)
                        question = await ask.reactionwait(ctx, message)

                        if question == "proceed":
                            level = i - 1
                            desired_level = result[1] + i - 1
                            upgrade_Cost = i - 1
                            break
                        if question == "cancel":
                            print(f"{ctx.author.name} - skillup - skill:{skill} partial level up cancelled")
                            emoji = "<:annoy:1412540836167684116>"
                            return "Fail", f"❌ {emoji} skill up canceled!"
                        if question == "timeout":
                            print(f"{ctx.author.name} - skillup - skill:{skill} timeout")
                            emoji = "<:zlowenergy:1412527768540811325>"
                            return "Fail", f"{emoji} timeout!!"

                #upgrade is possible
                print(f"skill:{skill} || level:{level} || desired_level:{desired_level} || skill_points:{skill_points} || upgrade_Cost:{upgrade_Cost}")
                if skill_points >= upgrade_Cost:
                    print(f"{ctx.author.name} - skillup - skill:{skill} level up confirmed")
                    print(f"{ctx.author.name} - skillup - skill:{skill} get skill value from database")
                    cur.execute("UPDATE ddc_player SET skill_points = {}, {} = {} WHERE player_id = {}".format(skill_points - level, skill + "_skill", desired_level, ctx.author.id))
                    print(f"{ctx.author.name} - skillup - skill:{skill} success - send message")
                    emoji = "<:angle:1412540828701823007>"
                    return "Pass", f"✅ {emoji} {skill} has been upgraded to {desired_level}!\n {skill_points - level} skill points left"

async def setup(bot):
    await bot.add_cog(userskillup(bot))