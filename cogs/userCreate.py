from discord.ext import commands
import psycopg2
from datetime import date
import userExistCheck, messageSend

class usercreate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="create", description="Create a character")
    async def create(self,ctx):
        print(f"{ctx.author.name} - create")
        #check if user already exist
        print(f"{ctx.author.name} - create - check if user exists")
        if userExistCheck.userExist(ctx.author.id) == "not found":
            #trigger function to add new user
            print(f"{ctx.author.name} - create - user not found - add to database")
            await dbinsert(ctx)
            #define message and trigger message send function
            print(f"{ctx.author.name} - create - post success message")
            emoji = "<:angle:1412540828701823007>"
            message = f"✅ {emoji} new character has been created!"
            await messageSend.postMessage(ctx,message,"Pass")


        else:
            print(f"{ctx.author.name} - create - user already exists - post fail message")
            # define message and trigger message send function

            emoji = "<:annoy:1412540836167684116>"
            message = f"❌ {emoji} your character already exists!"
            await messageSend.postMessage(ctx, message, "Fail")


async def dbinsert(ctx):
    try:
        #insert new line to the DB
        print(f"{ctx.author.name} - create - log into database")
        with psycopg2.connect(dbname="Discord_DDC", user="postgres", password="1234") as conn:
            with conn.cursor() as cur:
                print(f"{ctx.author.name} - create - adding user to database")
                cur.execute("INSERT INTO ddc_player (player_id, player_name, date, action) VALUES (%s, %s,%s, %s)",
                            (ctx.author.id, ctx.author.name, date.today(), 20))
    except (Exception, psycopg2.Error) as error:
        print(error)

async def setup(bot):
    await bot.add_cog(usercreate(bot))