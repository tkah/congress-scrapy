import csv
import psycopg2
import json
import datetime
from config import config

db_params = config('postgresql')

conn = psycopg2.connect(**db_params)
cur = conn.cursor()

with open('data/Dailykospres.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        details = {}
        detailsArray = []

        if "-" not in row[0]:
            continue

        state, district = row[0].split("-")
        incumbent = row[1]
        party = row[2]
        clinton = row[3]
        trump = row[4]
        obama2012 = row[5]
        romney = row[6]
        obama2008 = row[7]
        mccain = row[8]

        if district == "AL":
            district = "00"

        details["year"] = "2016"
        details["republican"] = {}
        details["republican"]["candidate"] = "Trump"
        details["republican"]["percentage"] = trump
        details["democrat"] = {}
        details["democrat"]["candidate"] = "Clinton"
        details["democrat"]["percentage"] = clinton
        detailsArray.append(details)

        details = {}
        details["year"] = "2012"
        details["republican"] = {}
        details["republican"]["candidate"] = "Romney"
        details["republican"]["percentage"] = romney
        details["democrat"] = {}
        details["democrat"]["candidate"] = "Obama"
        details["democrat"]["percentage"] = obama2012
        detailsArray.append(details)

        details = {}
        details["year"] = "2008"
        details["republican"] = {}
        details["republican"]["candidate"] = "McCain"
        details["republican"]["percentage"] = mccain
        details["democrat"] = {}
        details["democrat"]["candidate"] = "Obama"
        details["democrat"]["percentage"] = obama2008
        detailsArray.append(details)

        d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sql = """INSERT INTO public."Districts" (id, state, number, presidential_votes, "createdAt", "updatedAt")
            VALUES (%s, %s, %s, %s, %s, %s)"""

        cur.execute(sql, (
            state + district,
            state,
            district,
            json.dumps(detailsArray),
            d,
            d
        ))
    conn.commit()

with open('data/20m_PP_Scores.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        details = {}
        detailsArray = []

        if row[0] == "STATEFP":
            continue

        fips = row[0]
        district = row[1]
        gerrymander_score = 100 - int(row[8])

        cur.execute("""SELECT id FROM public."States" WHERE fips_code = %s""", (fips,))
        state = cur.fetchone()[0]

        sql = """UPDATE public."Districts"
                    SET gerrymander_score = %s
                    WHERE id = %s"""

        cur.execute(sql, (
            gerrymander_score,
            state + district
        ))
    conn.commit()
cur.close()
