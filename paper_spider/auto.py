import subprocess
import time
import os
from utils import get_proxies, refresh_proxies, check_missing_journals
import re
import json
def update_skipped():
    with open('log.txt', 'r') as f:
        log = f.read()
        result = re.findall('WARNING: Failed to parse search result of (.*) http', log)
        # existed = re.findall('\[paper_spider.pipelines\] INFO: Journal (.*) existed.', log)
        # mismatch = re.findall('Succeed to parse detail url of (.*): \./index\.php\?j', log)
    with open('skipped.json', 'r') as f:
        skipped = json.loads(f.read())
    with open('skipped.json', 'w') as f:
        skipped += result
        # skipped += existed
        # skipped += mismatch
        skipped = list(set(skipped))
        f.write(json.dumps(skipped))

try:
    update_skipped()
    check_missing_journals()
    os.remove('log.txt')
except:
    pass


# refresh_proxies()
# time.sleep(5)
get_proxies()
start = time.time()

spider = subprocess.Popen(['scrapy', 'crawl', 'journals'])

try:
    while True:
        poll = spider.poll()
        if poll is not None:
            break
        if time.time() - start < 60 * 60:
            time.sleep(5)
            continue
        spider.terminate()
        spider.wait()

        update_skipped()
        check_missing_journals()
        os.remove('log.txt')
        refresh_proxies()
        time.sleep(5)
        get_proxies()
        spider = subprocess.Popen(['scrapy', 'crawl', 'journals'])
        start = time.time()
        
except:
    spider.terminate()
    