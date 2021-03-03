import subprocess
import time
import os
from utils import get_proxies, refresh_proxies

try:
    os.remove('log.txt')
except:
    pass
refresh_proxies()
time.sleep(5)
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

        os.remove('log.txt')
        refresh_proxies()
        time.sleep(5)
        get_proxies()
        spider = subprocess.Popen(['scrapy', 'crawl', 'journals'])
        start = time.time()
        
except:
    spider.terminate()
    