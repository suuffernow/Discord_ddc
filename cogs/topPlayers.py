from table2ascii import table2ascii as t2a, PresetStyle, Alignment
from discord.ext import commands
import psycopg2, discord, os
import messageSend
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

class top(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="top", description="Display top X players")
    async def top(self, ctx, x=5):
        try:
            print(f"XX - profile - log into database")
            # pull data for the user
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT player_name, exploration FROM ddc_player ORDER BY exploration DESC")
                    playerList = cur.fetchall()
                    if len(playerList) < x:
                        x = len(playerList)

                    playerTable = []
                    for i in range(x):
                        playerTable += [f"#{i+1}", playerList[i][0], playerList[i][1]],
                    print(playerTable)

                    topTable = t2a(
                        header=["#", "Name", "Exploration"],
                        body=playerTable,
                        alignments=[Alignment.CENTER, Alignment.CENTER, Alignment.CENTER],
                        style=PresetStyle.double_thin_box)

                    print(f"{ctx.author.name} - topX - post leaderboard")
                    await messageSend.postMessage(ctx, f"```\n{topTable}\n```", "Info")

        except (Exception, psycopg2.Error) as error:
            print(error)

async def setup(bot):
    await bot.add_cog(top(bot))