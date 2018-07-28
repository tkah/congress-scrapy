"""
    Grab members from Github, get their Propublica data and write it back to DB
"""
import psycopg2
import urllib.parse
import json
import datetime
from config import config
from urllib.request import Request, urlopen

PROPUBLICA_URL = 'https://api.propublica.org/congress/v1/members/'
GIT_CURRENT_MEMBERS = 'https://theunitedstates.io/congress-legislators/legislators-current.json'
GOOGLE_CIVIC_API = 'https://www.googleapis.com/civicinfo/v2/representatives/' + urllib.parse.quote_plus('ocd-division/country:us/state:')

git_res = urlopen(GIT_CURRENT_MEMBERS)
git_members = json.loads(git_res.read().decode())

google_civic_key = config('keys')['google_civic_key']
propublica_key = config('keys')['propublica_key']
congress_num = config('congress')['number']
db_params = config('postgresql')

conn = psycopg2.connect(**db_params)
cur = conn.cursor()

cur.execute('SELECT id FROM public."Members"')
members = cur.fetchall()

headers = { "X-API-Key": propublica_key }

for mem in git_members:
    member_id = mem['id']['bioguide']
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
                    committees = %s,
                    thomas_id = %s,
                    lis_id = %s,
                    nickname = %s
            WHERE   id = %s"""

    nickname = None
    if 'nickname' in mem['name']:
        nickname = mem['name']['nickname']

    lis = None
    if 'lis' in mem['id']:
        lis = mem['id']['lis']

    thomas = None
    if 'thomas' in mem['id']:
        lis = mem['id']['thomas']

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
        thomas,
        lis,
        nickname,
        member_id
    ))
    conn.commit()

d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
cur.execute("""SELECT id FROM public."States" """)
states = cur.fetchall()

for state in states:
    abb = state[0].lower()

    if abb == "al":
        req_url = GOOGLE_CIVIC_API + abb + "?alt=json&key=" + google_civic_key
        response = None

        try:
            response = urlopen(req_url)
        except HTTPError as e:
            print('Error code: ', e.code)
            continue

        json_res = json.loads(response.read().decode())
        offices = json_res['offices']
        officials = json_res['officials']

        for office in offices:
            if "United States" in office['name']:
                continue

            officialIndex = office['officialIndices'][0]
            title = office['name']
            member = officials[officialIndex]
            photo_url = None
            party = None
            twitter_account = None
            youtube_account = None
            facebook_account = None
            email = None
            office = None
            phone = None
            address = ""
            url = None
            city = member['address'][0]['city']
            zip = member['address'][0]['zip']

            name_parts = member['name'].split(" ")
            first_name = " ".join(name_parts[0:(len(name_parts) - 1)])
            last_name = name_parts[len(name_parts) - 1]

            for key, value in member['address'][0].items():
                if "line" in key:
                    address += value + "::"

            if 'channels' in member:
                for channel in member['channels']:
                    if channel['type'] == 'Facebook':
                        facebook_account = channel['id']
                    elif channel['type'] == 'YouTube':
                        youtube_account = channel['id']
                    elif channel['type'] == 'Twitter':
                        twitter_account = channel['id']

            if 'photoUrl' in member:
                photo_url = member['photoUrl']

            if 'party' in member:
                party = member['party']

            if 'emails' in member:
                email = member['emails'][0]

            if 'urls' in member:
                url = member['urls'][0]

            if 'phones' in member:
                phone = member['phones'][0]

            sql = """INSERT INTO public."Members" (
                id,
                url,
                youtube_account,
                twitter_account,
                facebook_account,
                title,
                office,
                zip,
                city,
                party,
                phone,
                photo_url,
                first_name,
                last_name,
                email,
                "createdAt",
                "updatedAt")
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s)"""

            cur.execute(sql, (
                abb + "_" + title.replace(" ", "_"),
                url,
                youtube_account,
                twitter_account,
                facebook_account,
                title,
                address,
                zip,
                city,
                party,
                phone,
                photo_url,
                first_name,
                last_name,
                email,
                d,
                d
            ))
            conn.commit()

sql = """INSERT INTO public."Members" (
        id,
        date_of_birth,
        gender,
        url,
        twitter_account,
        facebook_account,
        title,
        short_title,
        start_date,
        end_date,
        body,
        office,
        contact_form,
        party,
        phone,
        photo_url,
        first_name,
        last_name,
        "createdAt",
        "updatedAt")
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s)"""

cur.execute(sql, (
    "President",
    "1946-06-14",
    "M",
    "https://www.donaldjtrump.com/",
    "https://twitter.com/realDonaldTrump",
    "https://www.facebook.com/DonaldTrump/",
    "President",
    "Pres.",
    "2017-01-20",
    "2021-01-20",
    "executive",
    "1600 Pennsylvania Avenue NW",
    "https://www.whitehouse.gov/contact/",
    "R",
    "202-456-1111",
    "https://www.whitehouse.gov/sites/whitehouse.gov/files/images/45/PE%20Color.jpg",
    "Donald",
    "Trump",
    d,
    d
))
conn.commit()

sql = """INSERT INTO public."Members" (
        id,
        date_of_birth,
        gender,
        url,
        twitter_account,
        facebook_account,
        title,
        short_title,
        start_date,
        end_date,
        body,
        office,
        contact_form,
        party,
        phone,
        photo_url,
        first_name,
        last_name,
        "createdAt",
        "updatedAt")
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s)"""

cur.execute(sql, (
    "VicePresident",
    "1959-06-07",
    "M",
    "https://www.whitehouse.gov/people/mike-pence/",
    "https://twitter.com/mike_pence?lang=en",
    "https://www.facebook.com/mikepence/",
    "Vice President",
    "Vice Pres.",
    "2017-01-20",
    "2021-01-20",
    "executive",
    "1600 Pennsylvania Avenue NW",
    "https://www.whitehouse.gov/contact/",
    "R",
    "202-456-1111",
    "https://www.whitehouse.gov/sites/whitehouse.gov/files/images/45/VPE%20Color.jpg",
    "Mike",
    "Pence",
    d,
    d
))
conn.commit()

cur.close()
