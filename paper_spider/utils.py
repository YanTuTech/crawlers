def get_journals():
    with open('journals.csv', 'r') as f:
        lines = f.readlines()[1:]
    
    for line in lines:
        title, impact_factor = line.split(',')
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
