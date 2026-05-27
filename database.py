import psycopg2
import pandas as pd
def postgres_connection():

    try:
        conn = psycopg2.connect(
            host="postgres.lab.karpov.courses",
            port=6432,
            database="startml",
            user="robot-startml-ro",
            password="pheiph0hahj1Vaif",
        )
    except Exception :
        print("❌ Ошибка при подключении к базе данных.")
        raise

    conn.autocommit = True

    return conn

cur = postgres_connection()
goo = cur.cursor()
goo.execute("""
SELECT * 
FROM public.user 
WHERE id = 21
""")
row = goo.fetchone()
df = pd.read_sql(
    "SELECT * FROM public.user  ",
    cur
)
