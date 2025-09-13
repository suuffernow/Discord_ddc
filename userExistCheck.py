import psycopg2, os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

def userExist(Discord_ID):
    #check if user exist in DB
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ddc_player WHERE player_id = %s", [Discord_ID])
            if cur.fetchone() == None:
                return "not found"
            else:
                return "found"



