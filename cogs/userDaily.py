from discord.ext import commands
import psycopg2, os
from datetime import date
import userExistCheck, messageSend
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

class userdaily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="daily", description="Get daily actions")
    async def userdaily(self, ctx):
        print(f"{ctx.author.name} - daily")
        #check if user already exist
        print(f"{ctx.author.name} - daily - check if user exists")
        if userExistCheck.userExist(ctx.author.id) == "found":
            #trigger function to add new user
            print(f"{ctx.author.name} - daily - user found - update to database")
            result = await dbupdate(ctx)

        else:     #if user doesnt exist inform user
            print(f"{ctx.author.name} - daily - user not found - post failed message")
            emoji = "<:annoy:1412540836167684116>"
            result = ["Fail", f"❌ {emoji} your character doesn't exists!"]

        await messageSend.postMessage(ctx, result[1], result[0])

async def dbupdate(ctx):
    try:
        print(f"{ctx.author.name} - daily - log into database")
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                #get current user data
                print(f"{ctx.author.name} - daily - pull data from database")
                cur.execute("SELECT * FROM ddc_player WHERE player_id = %s", [ctx.author.id])
                result = cur.fetchone()
                #compare date in player sheet and current date
                print(f"{ctx.author.name} - daily - check if command was used today")
                if result[2] < date.today():
                    action = result[3] + 10
                    print(f"{ctx.author.name} - daily - command not used yet - update database")
                    cur.execute("UPDATE ddc_player SET action = %s, date = %s where player_id = %s",
                                [action, date.today(), ctx.author.id])
                    print(f"{ctx.author.name} - daily - post success message")
                    emoji = "<:angle:1412540828701823007>"
                    message = f"✅ {emoji} daily action has been added!\nYou currently have {action} actions!"
                    return "Pass", message
                else:
                    print(f"{ctx.author.name} - daily - post fail message")
                    emoji = "<:debil:1412540842660335676>"
                    message = f"❌ {emoji} command already used today"
                    return "Fail", message

    except (Exception, psycopg2.Error) as error:
        print(error)

async def setup(bot):
    await bot.add_cog(userdaily(bot))