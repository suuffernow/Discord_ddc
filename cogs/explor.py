import random, psycopg2, asyncio, os
from discord.ext import commands
from combat import fighter, combat
import userExistCheck, messageSend
from explor_history import explor_history
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


class explor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="explore", brief="Explore the dungeon")
    async def explore(self, ctx, level: int | None = None):
        print(f"{ctx.author.name} - explore")
        # check if user already exist
        print(f"{ctx.author.name} - explore - check if user exists")
        if userExistCheck.userExist(ctx.author.id) == "found":
            # trigger function to add new user
            print(f"{ctx.author.name} - explore - user found")
            if level is None:
                print(f"{ctx.author.name} - explore - define max explore level")
                with psycopg2.connect(DATABASE_URL) as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT exploration FROM ddc_player WHERE player_id = %s", [ctx.author.id])
                        result = cur.fetchone()
                        level = result[0] + 1
                        print(f"{ctx.author.name} - explore - level changed to {level}")

            print(f"{ctx.author.name} - explore - start exploration on level:{level}")
            result = await self.explorelevel(ctx, level)

        else:  # user doesnt exist
            print(f"{ctx.author.name} - explore - user does not exist")
            emoji = "<:annoy:1412540836167684116>"
            result = ["Fail", f"❌ {emoji} your character doesn't exist!"]

        await messageSend.postMessage(ctx, result[1], result[0])

        if result[0] == "Pass" and level % 5 == 0:
            from cogs.bossDrops import bossdrops
            drop = bossdrops(bot=self.bot)
            await drop.drops(level, ctx)

        await explor_history(ctx, level, result)

    async def explorelevel(self, ctx, level):
        print(f"{ctx.author.name} - explore - log into database")
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                # define player stats and stats multipliers for skill + equipment
                print(f"{ctx.author.name} - explore - get user data + equipment")
                cur.execute("SELECT * FROM ddc_player WHERE player_id = %s", [ctx.author.id])
                player_stats = cur.fetchone()

                # check exploration level available
                print(f"{ctx.author.name} - explore - check if player have enough actions")
                if player_stats[3] <= 0:
                    print(f"{ctx.author.name} - explore - not enough actions")
                    emoji = "<:debil:1412540842660335676>"
                    return "Fail", f"❌ {emoji} You don't have enough actions. Come back tomorrow!"

                print(f"{ctx.author.name} - explore - check if exploration level is within allowed range")
                if player_stats[4] + 1 < level:
                    print(f"{ctx.author.name} - explore - exploration level to high")
                    emoji = "<:debil:1412540842660335676>"
                    return "Fail", f"❌ {emoji}{emoji} You cannot explore that far scrub! Go challenge someone on your level\n{emoji}{emoji} Max explore level is {player_stats[4] + 1}"

                # remove 1 action
                print(f"{ctx.author.name} - explore - remove 1 action from the user")
                cur.execute("UPDATE ddc_player SET action = %s WHERE player_id= %s",[player_stats[3] - 1, ctx.author.id])

                # assign stats * their multiplier
                print(f"{ctx.author.name} - explore - calculate player stats")
                player_atk = player_stats[10] + player_stats[10] * ((player_stats[15] + player_stats[20] + player_stats[
                    25] + player_stats[30] + player_stats[35] + player_stats[40]) / 100)
                player_hp = player_stats[11] + player_stats[11] * ((player_stats[16] + player_stats[21] + player_stats[
                    26] + player_stats[31] + player_stats[36] + player_stats[41]) / 100)
                player_dex = player_stats[12] + player_stats[12] * ((player_stats[17] + player_stats[22] + player_stats[
                    27] + player_stats[32] + player_stats[37] + player_stats[42]) / 100)
                player_spd = player_stats[13] + player_stats[13] * ((player_stats[18] + player_stats[23] + player_stats[
                    28] + player_stats[33] + player_stats[38] + player_stats[43]) / 100)

                # define oponent stats
                print(f"{ctx.author.name} - explore - calculate enemy stats")
                cur.execute("SELECT * FROM enemy_stats WHERE level = %s", [level])
                oponent_stats = cur.fetchone()
                oponent_atk = oponent_stats[2]
                oponent_hp = oponent_stats[3]
                oponent_dex = oponent_stats[4]
                oponent_spd = oponent_stats[5]

                # randomize enemy name
                print(f"{ctx.author.name} - explore - get enemy name")
                if level % 5 == 0:
                    cur.execute("SELECT boss FROM enemy_names WHERE boss IS NOT NULL")
                    oponent_name = random.choice(cur.fetchall())
                    oponent_name = "☠️ " + oponent_name[0]
                    print(f"{ctx.author.name} - explore - BOSS name defined {oponent_name}")
                else:
                    cur.execute("SELECT type, name FROM enemy_names WHERE boss IS NULL")
                    oponent_name = random.choice(cur.fetchall())
                    oponent_name = oponent_name[0] + " - " + oponent_name[1]
                    print(f"{ctx.author.name} - explore - trash moob name defined {oponent_name}")

                # set up charatcers and their stats
                print(f"{ctx.author.name} - explore - create fighter objects for player and opponent")
                oponent = fighter(oponent_name, oponent_atk, oponent_hp, oponent_dex, player_dex)
                player = fighter(ctx.author.name, player_atk, player_hp, player_dex, oponent_dex)

                # define first strike
                print(f"{ctx.author.name} - explore - start a fight")
                battle = combat()
                emoji = "<:shark:1412540848922427452>"
                message_string = f"{emoji}{emoji} {ctx.author.name} encountered {oponent_name} on level {level}!"
                message = await messageSend.postMessage(ctx, message_string, "Combat")

                FS = random.randint(1, 1000) + player_spd - oponent_spd
                if FS > 400:
                    print(f"{ctx.author.name} - explore - player first move")
                    await asyncio.sleep(1)
                    message_string += f"\n\n {ctx.author.name} attacks first!!"
                    await messageSend.postMessage(ctx, message_string, "Combat2", message)
                    victory = await battle.start_fight(player, oponent, message, message_string, ctx)
                else:
                    print(f"{ctx.author.name} - explore - enemy first move")
                    await asyncio.sleep(1)
                    message_string += f"\n\n {oponent_name} attacks first!!"
                    await messageSend.postMessage(ctx, message_string, "Combat2", message)
                    victory = await battle.start_fight(oponent, player, message, message_string, ctx)

                if victory == ctx.author.name:
                    print(f"{ctx.author.name} - explore - enemy defeated")
                    new_exp = player_stats[5] + level
                    new_skills = player_stats[14] + 1
                    emoji = "<:zrage:1412527734650830908>"
                    level_update = level
                    if level_update < player_stats[4]:
                        level_update = player_stats[4]
                    if level % 5 == 0:
                        print(f"{ctx.author.name} - explore - boss kill acknowledged")
                        cur.execute("UPDATE ddc_player SET exp = {}, exploration = {}, skill_points = {} WHERE player_id= {}".format(new_exp, level_update, new_skills, ctx.author.id))

                        return "Pass", f"{ctx.author.name}\n{emoji}{emoji}{emoji}{emoji} Level {level} has been cleared! You have obtained {level} exp and a Skill Point for defeating a boss!!", oponent_name

                    else:
                        print(f"{ctx.author.name} - explore - trash moob kill acknowledged")
                        cur.execute("UPDATE ddc_player SET exp = {}, exploration = {} WHERE player_id= {}".format(new_exp,level_update,ctx.author.id))

                        return "Pass", f"{ctx.author.name}\n{emoji}{emoji} Level {level} has been cleared! You have obtained {level} exp!", oponent_name
                else:
                    emoji = "<:zlowenergy:1412527768540811325>"
                    emoji2 = "<:zimfine:1412527823884648561>"
                    return "Fail", f"️{emoji}{emoji} You have been defeated, better luck next time! {emoji2}{emoji2}", oponent_name

async def setup(bot):
    await bot.add_cog(explor(bot))