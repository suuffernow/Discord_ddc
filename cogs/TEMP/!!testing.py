import textwrap

import psycopg2
import random
from table2ascii import table2ascii as t2a, PresetStyle

def test01(date, Discord_ID):
    with psycopg2.connect(dbname="Discord_DDC", user="postgres", password="1234") as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE ddc_player SET action = %s where player_id = %s",[50, Discord_ID])
test01("2025-08-30", 237235863191289856)

#def testUpdate():
    #armor = textwrap.wrap("Peacekeeper_Linen_Jerkin", width=10, break_long_words=True)
    #print(armor)
#testUpdate()
