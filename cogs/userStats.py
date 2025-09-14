from table2ascii import table2ascii as t2a, PresetStyle, Merge, Alignment
from discord.ext import commands
import psycopg2, discord, os
import userExistCheck, messageSend
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


class userstats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="profile", description="Display self or someones profile")
    async def userprofile(self, ctx, player: discord.User | None ):
        print(f"{ctx.author.name} - profile")
        if player is None:
            player_id = ctx.author.id
            player = ctx.author
        else:
            player_id = player.id
        print(f"{ctx.author.name} - profile - set user to display to {player}")
        # check if user exists
        print(f"{ctx.author.name} - profile - check if {player} exists")
        if userExistCheck.userExist(player_id) == "found":
            print(f"{ctx.author.name} - profile - {player} get user data")
            result = await getdata(player_id, player)

        else:
            print(f"{ctx.author.name} - profile - {player} does not exist")
            emoji = "<:annoy:1412540836167684116>"
            result = ["Fail", f"❌ {emoji} character doesn't exist!"]

        await messageSend.postMessage(ctx, result[1], result[0])


async def getdata(player_id, player):
    try:
        print(f"XX - profile - log into database")
        # pull data for the user
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                print(f"XX - profile - pull data for {player}")
                cur.execute("SELECT * FROM ddc_player WHERE player_id = %s", [player_id])
                stats = cur.fetchone()

                # create table with stats
                print(f"XX - profile - create stats table for {player}")
                statsUser = (
                    f"{player}\nExplored up to floor: {stats[4]} -=- Actions available: {stats[3]}\nEXP available: {stats[5]} -=- Skill points available: {stats[14]}")
                statsTable = t2a(
                    header=["ATK", "HP", "DEX", "SPD"],
                    body=[
                        ["levelUp", Merge.LEFT, Merge.LEFT, Merge.LEFT],
                        [stats[6], stats[7], stats[8], stats[9]],
                        ["skillUp", Merge.LEFT, Merge.LEFT, Merge.LEFT],
                        [f"+ {stats[15]}%", f"+ {stats[16]}%", f"+ {stats[17]}%", f"+ {stats[18]}%"],
                        [" ", Merge.LEFT, Merge.LEFT, Merge.LEFT],
                        ["weapon: "+stats[19],Merge.LEFT, Merge.LEFT, Merge.LEFT],
                        [f"+ {stats[20]}%", f"+ {stats[21]}%", f"+ {stats[22]}%",f"+ {stats[23]}%"],
                        ["armor: "+stats[24], Merge.LEFT, Merge.LEFT, Merge.LEFT],
                        [f"+ {stats[25]}%", f"+ {stats[26]}%", f"+ {stats[27]}%",f"+ {stats[28]}%"],
                        ["pants: "+stats[29], Merge.LEFT, Merge.LEFT, Merge.LEFT],
                        [f"+ {stats[30]}%", f"+ {stats[31]}%", f"+ {stats[32]}%",f"+ {stats[33]}%"],
                        ["gloves: "+stats[34], Merge.LEFT, Merge.LEFT, Merge.LEFT],
                        [f"+ {stats[35]}%", f"+ {stats[36]}%", f"+ {stats[37]}%",f"+ {stats[38]}%"],
                        ["boots: "+stats[39], Merge.LEFT, Merge.LEFT, Merge.LEFT],
                        [f"+ {stats[40]}%", f"+ {stats[41]}%", f"+ {stats[42]}%", f"+ {stats[43]}%"]
                    ],
                    column_widths=[12, 12, 12, 12],
                    alignments=[Alignment.CENTER, Alignment.CENTER, Alignment.CENTER, Alignment.CENTER],
                    style=PresetStyle.double_thin_box)

                print(f"XX - profile - post stats table for {player}")
                message = (f"{statsUser}\n\n{statsTable}")
                return "Info", f"```\n{message}\n```"

    except (Exception, psycopg2.Error) as error:
        print(error)

async def setup(bot):

    await bot.add_cog(userstats(bot))
