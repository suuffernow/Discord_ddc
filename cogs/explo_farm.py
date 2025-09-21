import random, psycopg2, asyncio, os
from discord.ext import commands
from combat import fighter, combat
import userExistCheck, messageSend
from explor_history import explor_history
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')



class farm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="farm", brief="Explore the dungeon level multiple times")
    async def farm(self, ctx, level: int, times: int):
        print(f"{ctx.author.name} - farm")
        # check if user already exist
        print(f"{ctx.author.name} - farm - check if user exists")
        if userExistCheck.userExist(ctx.author.id) == "found":
            print(f"{ctx.author.name} - farm - user found")
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT exploration, action FROM ddc_player WHERE player_id = %s", [ctx.author.id])
                    explo_action = cur.fetchone()
                    print(f"{ctx.author.name} - farm - available level / actions:{explo_action}")

            if level % 5 == 0:
                emoji = "<:annoy:1412540836167684116>"
                print(f"{ctx.author.name} - farm - attempt to farm boss")
                result = ["Fail", f"❌ {emoji} you cannot farm boss levels"]
            elif explo_action[0] < level:
                emoji = "<:annoy:1412540836167684116>"
                print(f"{ctx.author.name} - farm - attempt to farm too high level")
                result = ["Fail", f"❌ {emoji} you cannot farm not yet cleared level!"]
            elif explo_action[1] < times:
                emoji = "<:annoy:1412540836167684116>"
                print(f"{ctx.author.name} - farm - not enough actions")
                result = ["Fail", f"❌ {emoji} not enough actions to farm that! \n You have {explo_action[1]} actions remaining"]
            else:
                result = await self.explofarm(ctx, level, times)

        else:  # user doesnt exist
            print(f"{ctx.author.name} - farm - user does not exist")
            emoji = "<:annoy:1412540836167684116>"
            result = ["Fail", f"❌ {emoji} your character doesn't exist!"]

        await messageSend.postMessage(ctx, result[1], result[0])

    async def explofarm(self, ctx, level, times):
        print(f"{ctx.author.name} - farm - log into database")
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                # define player stats and stats multipliers for skill + equipment
                print(f"{ctx.author.name} - explore - get user data + equipment")
                cur.execute("SELECT * FROM ddc_player WHERE player_id = %s", [ctx.author.id])
                player_stats = cur.fetchone()

                # assign stats * their multiplier
                print(f"{ctx.author.name} - explore - calculate player stats")
                player_atk = player_stats[10] + player_stats[10] * ((player_stats[15] + player_stats[20] + player_stats[
                    25] + player_stats[30] + player_stats[35] + player_stats[40] + player_stats[45]) / 100)
                player_hp = player_stats[11] + player_stats[11] * ((player_stats[16] + player_stats[21] + player_stats[
                    26] + player_stats[31] + player_stats[36] + player_stats[41] + player_stats[46]) / 100)
                player_dex = player_stats[12] + player_stats[12] * ((player_stats[17] + player_stats[22] + player_stats[
                    27] + player_stats[32] + player_stats[37] + player_stats[42] + player_stats[47]) / 100)
                player_spd = player_stats[13] + player_stats[13] * ((player_stats[18] + player_stats[23] + player_stats[
                    28] + player_stats[33] + player_stats[38] + player_stats[43] + player_stats[48]) / 100)

                # define oponent stats
                print(f"{ctx.author.name} - explore - calculate enemy stats")
                cur.execute("SELECT * FROM enemy_stats WHERE level = %s", [level])
                oponent_stats = cur.fetchone()
                oponent_atk = oponent_stats[2]
                oponent_hp = oponent_stats[3]
                oponent_dex = oponent_stats[4]
                oponent_spd = oponent_stats[5]

                # randomize enemy name
                cur.execute("SELECT type, name FROM enemy_names WHERE boss IS NULL")
                oponent_name = random.choice(cur.fetchall())
                oponent_name = oponent_name[0] + " - " + oponent_name[1]
                print(f"{ctx.author.name} - explore - trash moob name defined {oponent_name}")

                # set up charatcers and their stats
                print(f"{ctx.author.name} - explore - create fighter objects for player and opponent")
                oponent = fighter(oponent_name, oponent_atk, oponent_hp, oponent_dex, player_dex)
                player = fighter(ctx.author.name, player_atk, player_hp, player_dex, oponent_dex)

                print(f"{ctx.author.name} - explore - start a fight")
                battle = combat()
                emoji = "<:shark:1412540848922427452>"
                message_string = f"{emoji}{emoji} {ctx.author.name} started {times} fights on level {level}!"
                message_string2 = message_string
                message = await messageSend.postMessage(ctx, message_string, "Combat")

                # remove X actions
                print(f"{ctx.author.name} - explore - remove 1 action from the user")
                cur.execute("UPDATE ddc_player SET action = %s WHERE player_id= %s",[player_stats[3] - times, ctx.author.id])
                total_xp = 0
                new_exp = player_stats[5]
                for i in range(times):
                    await asyncio.sleep(5)

                    FS = random.randint(1, 1000) + player_spd - oponent_spd
                    if FS > 400:
                        victory = await battle.start_fight(player, oponent, message, message_string, ctx)
                    else:
                        victory = await battle.start_fight(oponent, player, message, message_string, ctx)

                    if victory == ctx.author.name:
                        new_exp +=  level
                        total_xp += level
                        emoji = "<:zrage:1412527734650830908>"
                        print(f"{ctx.author.name} - explore - trash moob kill acknowledged")
                        message_string2 += f"\n✅{i+1:} {emoji} exploration successful!"
                        await asyncio.sleep(5)
                        await messageSend.postMessage(ctx, message_string2, "Combat2", message)
                        result = ["Pass","",oponent_name]

                    else:
                        emoji = "<:zlowenergy:1412527768540811325>"
                        emoji2 = "<:zimfine:1412527823884648561>"
                        message_string2 += f"\n❌{i + 1:} {emoji}{emoji2} exploration failed!"
                        await asyncio.sleep(5)
                        await messageSend.postMessage(ctx, message_string2, "Combat2", message)
                        result = ["Pass", "", oponent_name]
                    await explor_history(ctx, level, result)
                    i += 1
                cur.execute("UPDATE ddc_player SET exp = {} WHERE player_id= {}".format(new_exp, ctx.author.id))
        return "Pass", f"Completed {times} fights on level {level}. Total xp received: {total_xp}"


async def setup(bot):
    await bot.add_cog(farm(bot))