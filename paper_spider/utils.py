def get_full_journals():
    with open('journals.csv', 'r') as f:
    # with open('missingJournals.csv', 'r') as f:
        lines = f.readlines()[1:]
    
    for line in lines:
        title, impact_factor = line.split(',')
        yield [title, float(impact_factor)]

def get_journals():
    # with open('journals.csv', 'r') as f:
    with open('skipped.json', 'r') as f:
        skipped = json.loads(f.read())
    skipped = [journal.lower() for journal in skipped]
    with open('missingJournals.csv', 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        title, impact_factor = line.split(',')
        if title.lower() in skipped:
            continue
        yield [title, float(impact_factor)]


import requests
def get_proxies():
    response = requests.get("https://proxy.webshare.io/api/proxy/list/?page=1", headers={"Authorization": "Token bc85b045d7416e93dcb2c3e05f98df35ee01fb26"})
    data = response.json()['results']
    with open('proxies.txt', 'w') as f:
        for proxy in data:
            f.write(f"{proxy['proxy_address']}:{proxy['ports']['http']}\n")

def refresh_proxies():
    requests.post(
        "https://proxy.webshare.io/api/proxy/replacement/info/refresh/",
        headers={"Authorization": "Token bc85b045d7416e93dcb2c3e05f98df35ee01fb26"}
    )

import json
from db import Journal
def check_missing_journals():
    with open('skipped.json', 'r') as f:
        skipped = json.loads(f.read())
    skipped = [journal.lower() for journal in skipped]

    f = open('missingJournals.csv', 'w')
    journals = Journal.select()
    journals = [journal.name.lower() for journal in journals]

    for journal_name, if_ in get_full_journals():
        if journal_name.lower() in journals:
            continue
        if journal_name.lower() in skipped:
            continue
        f.write(f'{journal_name},{if_}\n')
    f.close()
