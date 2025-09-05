import psycopg2

def userExist(Discord_ID):
    #check if user exist in DB
    with psycopg2.connect(dbname="Discord_DDC", user="postgres", password="1234") as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ddc_player WHERE player_id = %s", [Discord_ID])
            if cur.fetchone() == None:
                return "not found"
            else:
                return "found"



