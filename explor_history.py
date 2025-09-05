from datetime import date
import psycopg2

async def explor_history(ctx, level, result):
    print(f" id: {ctx.author.id} || name: {ctx.author.name} || date: {date.today()} || level: {level} || result: {result[2]} / {result[0]}")
    try:
        if result[2]:
            print(f"{ctx.author.name} - history - add fight status to DB")
            with psycopg2.connect(dbname="Discord_DDC", user="postgres", password="1234") as conn:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO explo_history (player_id, player_name, date, level, enemy, status) VALUES (%s, %s,%s, %s, %s, %s)",
                                (ctx.author.id, ctx.author.name, date.today(), level, result[2], result[0]))
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    else:
        return
