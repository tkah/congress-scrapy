import psycopg2
import datetime
from config import config

db_params = config('postgresql')

conn = psycopg2.connect(**db_params)
cur = conn.cursor()

for line in open('data/state-fips.txt','r'):
    fips, abbrev, name, _, votes, population = line.split('|')

    if fips == 'STATE':
        continue

    d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sql = """INSERT INTO public."States" (id, fips_code, full_name, electoral_votes, population, "createdAt", "updatedAt")
            VALUES (%s, %s, %s, %s, %s, %s, %s)"""

    cur.execute(sql, (
        abbrev,
        fips,
        name,
        votes,
        population,
        d,
        d
    ))
    conn.commit()

cur.close()
