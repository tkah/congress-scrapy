"""
    Grab members from DB, get their Propublica data and write it back to DB
"""
import psycopg2
import json
from config import config
from urllib.request import Request, urlopen

PROPUBLICA_URL = 'https://api.propublica.org/congress/v1/members/'

propublica_key = config('keys')['propublica_key']
congress_num = config('congress')['number']
db_params = config('postgresql')

conn = psycopg2.connect(**db_params)
cur = conn.cursor()

cur.execute('SELECT id FROM public."Members"')
members = cur.fetchall()

headers = { "X-API-Key": propublica_key }

for mem in members:
    member_id = mem[0]
    req_url = PROPUBLICA_URL + member_id + '.json'
    response = urlopen(Request(req_url, None, headers))

    member = json.loads(response.read().decode())['results'][0]
    currentRole = None
    for role in member['roles']:
        if role['congress'] == congress_num:
            currentRole = role

    at_large = None
    if 'at_large' in currentRole:
        at_large = currentRole['at_large']

    committees = []
    if 'committees' in currentRole:
        for comm in currentRole['committees']:
            committees.append(json.dumps(comm))

    sql = """UPDATE public."Members"
                SET date_of_birth = %s,
                    gender = %s,
                    url = %s,
                    govtrack_id = %s,
                    cspan_id = %s,
                    votesmart_id = %s,
                    icpsr_id = %s,
                    twitter_account = %s,
                    facebook_account = %s,
                    youtube_account = %s,
                    crp_id = %s,
                    congress = %s,
                    title = %s,
                    short_title = %s,
                    leadership_role = %s,
                    fec_candidate_id = %s,
                    seniority = %s,
                    at_large = %s,
                    ocd_id = %s,
                    start_date = %s,
                    end_date = %s,
                    office = %s,
                    fax = %s,
                    contact_form = %s,
                    bills_sponsored = %s,
                    bills_cosponsored = %s,
                    missed_votes_pct = %s,
                    votes_with_party_pct = %s,
                    committees = %s
            WHERE   id = %s"""

    cur.execute(sql, (
        member['date_of_birth'],
        member['gender'],
        member['url'],
        member['govtrack_id'],
        member['cspan_id'],
        member['votesmart_id'],
        member['icpsr_id'],
        member['twitter_account'],
        member['facebook_account'],
        member['youtube_account'],
        member['crp_id'],
        currentRole['congress'],
        currentRole['title'],
        currentRole['short_title'],
        currentRole['leadership_role'],
        currentRole['fec_candidate_id'],
        currentRole['seniority'],
        at_large,
        currentRole['ocd_id'],
        currentRole['start_date'],
        currentRole['end_date'],
        currentRole['office'],
        currentRole['fax'],
        currentRole['contact_form'],
        currentRole['bills_sponsored'],
        currentRole['bills_cosponsored'],
        currentRole['missed_votes_pct'],
        currentRole['votes_with_party_pct'],
        committees,
        member_id
    ))
    conn.commit()
cur.close()
