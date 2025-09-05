import discord
from table2ascii import table2ascii as t2a, PresetStyle

async def postMessage(ctx, message, status, edit = None):
    try:
        if status == "Pass":
            embed_reply = discord.Embed(title=message, color=discord.Color.green())
        elif status == "Fail":
            embed_reply = discord.Embed(title=message, color=discord.Color.red())
        elif status == "Info":
            embed_reply = discord.Embed(description=message, color=discord.Color.purple())
        elif status == "Question":
            embed_reply = discord.Embed(description=message, color=discord.Color.gold())
        elif status == "Combat" or status == "Combat2":
            embed_reply = discord.Embed(description=message, color=discord.Color.blurple())

        if ctx.author.avatar:
            embed_reply.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
        else:
            embed_reply.set_author(name=f"{ctx.author.name}")

        if status == "Combat2":
            a = await edit.edit(embed=embed_reply)
        else:
            a = await ctx.send(embed=embed_reply)
        return a
    except (Exception) as error:
        print(error)