import os

import psycopg2, random
from discord.ext import commands
from table2ascii import table2ascii as t2a, PresetStyle, Alignment
import messageSend
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


class bossdrops(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def drops(self, level, ctx):
        print(f"{ctx.author.name} - drops - define drop category")

        drop_options = ("eq_weapon", "eq_armor", "eq_pants", "eq_gloves", "eq_boots", "eq_earring")
        eq = random.choice(drop_options)  # randomize equipment slot
        print(f"{ctx.author.name} - drops - drop selected: {eq}")

        drop_range = 0
        print(f"{ctx.author.name} - drops - opening drop table - {eq}")
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                # find all eq below current level
                print(f"{ctx.author.name} - drops - {eq} - find whole list of drops")
                cur.execute("SELECT * FROM {} WHERE level <= {}".format(eq, level))
                drops = cur.fetchall()
                # limit drop table to higher level
                for row in drops:
                    drop_range += row[0]
                print(f"{ctx.author.name} - drops - {eq} - limit drop range")
                drop_range = round(drop_range / len(drops), 0)
                cur.execute("SELECT * FROM {} WHERE level <= {} and level >= {}".format(eq, level, drop_range))
                drops = cur.fetchall()
                eq_reward = random.choice(drops)  # randomize reward
                print(f"{ctx.author.name} - drops - {eq} - drop selected: {eq_reward}")

                print(f"{ctx.author.name} - drops - get player stats")
                cur.execute("SELECT * FROM ddc_player WHERE player_id = {}".format(ctx.author.id))
                player_stats = cur.fetchone()
                player_eq = []
                print(f"{ctx.author.name} - drops - find which elements of player sheet to compare")
                if eq == "eq_weapon":
                    dropped_item = "weapon"
                    for i in range(19, 24):
                        player_eq.append(player_stats[i])
                elif eq == "eq_armor":
                    dropped_item = "armor"
                    for i in range(24, 29):
                        player_eq.append(player_stats[i])
                elif eq == "eq_pants":
                    dropped_item = "pants"
                    for i in range(29, 34):
                        player_eq.append(player_stats[i])
                elif eq == "eq_gloves":
                    dropped_item = "gloves"
                    for i in range(34, 39):
                        player_eq.append(player_stats[i])
                elif eq == "eq_boots":
                    dropped_item = "boots"
                    for i in range(39, 44):
                        player_eq.append(player_stats[i])
                elif eq == "eq_earring":
                    dropped_item = "earring"
                    for i in range(34, 49):
                        player_eq.append(player_stats[i])

                print(f"{ctx.author.name} - drops - create table with player EQ")
                dropEQ = t2a(
                    header=[f"{dropped_item}", "CURRENT", "NEW"],
                    body=[["ATK", f"{player_eq[1]}", f"{eq_reward[2]}"],
                          ["HP", f"{player_eq[2]}", f"{eq_reward[3]}"],
                          ["DEX", f"{player_eq[3]}", f"{eq_reward[4]}"],
                          ["SPD", f"{player_eq[4]}", f"{eq_reward[5]}"]
                          ],
                    alignments=[Alignment.CENTER, Alignment.CENTER, Alignment.CENTER],
                    style=PresetStyle.thin_compact)
                print(f"{dropEQ}")
                print(f"{ctx.author.name} - drops - ask to equip item")
                emoji = "<:owo:1412549557903949966>"
                message = f"{emoji} What is this??\nYou found **{dropped_item}** under the boss. Would you like to equip it\n\n```\n{dropEQ}\n```"

                from cogs.reactionWait import reactionwait
                ask = reactionwait(bot=self.bot)
                result = await ask.reactionwait(ctx, message)
                if result == "proceed":
                    print(f"{ctx.author.name} - exploration - equip new item")
                    if eq == "eq_weapon":
                        cur.execute(
                            "UPDATE ddc_player SET weapon_name = %s, atk_weapon = %s, hp_weapon = %s, dex_weapon = %s, spd_weapon = %s WHERE player_id = %s",(eq_reward[1], eq_reward[2], eq_reward[3], eq_reward[4], eq_reward[5], ctx.author.id))
                    elif eq == "eq_armor":
                        cur.execute(
                            "UPDATE ddc_player SET armor_name = %s, atk_armor = %s, hp_armor = %s, dex_armor = %s, spd_armor = %s WHERE player_id = %s",(eq_reward[1], eq_reward[2], eq_reward[3], eq_reward[4], eq_reward[5], ctx.author.id))
                    elif eq == "eq_pants":
                        cur.execute(
                            "UPDATE ddc_player SET pants_name = %s, atk_pants = %s, hp_pants = %s, dex_pants = %s, spd_pants = %s WHERE player_id = %s",(eq_reward[1], eq_reward[2], eq_reward[3], eq_reward[4], eq_reward[5], ctx.author.id))
                    elif eq == "eq_gloves":
                        cur.execute(
                            "UPDATE ddc_player SET gloves_name = %s, atk_gloves = %s, hp_gloves = %s, dex_gloves = %s, spd_gloves = %s WHERE player_id = %s",(eq_reward[1], eq_reward[2], eq_reward[3], eq_reward[4], eq_reward[5], ctx.author.id))
                    elif eq == "eq_boots":
                        cur.execute(
                            "UPDATE ddc_player SET boots_name = %s, atk_boots = %s, hp_boots = %s, dex_boots = %s, spd_boots = %s WHERE player_id = %s",(eq_reward[1], eq_reward[2], eq_reward[3], eq_reward[4], eq_reward[5], ctx.author.id))
                    elif eq == "eq_earring":
                        cur.execute(
                            "UPDATE ddc_player SET earring_name = %s, atk_earring = %s, hp_earring = %s, dex_earring = %s, spd_earring = %s WHERE player_id = %s",(eq_reward[1], eq_reward[2], eq_reward[3], eq_reward[4], eq_reward[5], ctx.author.id))

                    emoji = "<:angle:1412540828701823007>"
                    result = ["Pass",f"✅ {emoji} you have equipped your new item!"]

                if result == "cancel":
                    print(f"{ctx.author.name} - exploration - cancel equipment")
                    emoji = "<:debil:1412540842660335676>"
                    result = ["Fail", f"❌ {emoji} you threw {dropped_item} to the corner of the room and went further!"]

                if result == "timeout":
                    print(f"{ctx.author.name} - exploration - equipment timeout")
                    emoji = "<:zlowenergy:1412527768540811325>"
                    result = "Fail", f"{emoji} timeout!!"

        await messageSend.postMessage(ctx, result[1], result[0])

async def setup(bot):
    await bot.add_cog(bossdrops(bot))