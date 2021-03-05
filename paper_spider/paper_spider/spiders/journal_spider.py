import scrapy
import json
from bs4 import BeautifulSoup
from paper_spider.items import *
from utils import *
from db import Journal as JournalDB
from scrapy.http.request.form import FormRequest

class JournalsSpider(scrapy.Spider):
    name = "journals"

    def start_requests(self):
        journal_gen = get_journals()
        
        count = 0
        journals = JournalDB.select()
        journals = [journal.name.lower() for journal in journals]
        # start = False
        # last_name = ''
        # try:
        #     last_name = JournalDB.select().order_by(JournalDB.id.desc()).get().name
        # except:
        #     start = True
        for journal_name, impact_factor in journal_gen:
            # if not start and journal_name == last_name:
            #     start = True
            # if not start:
            #     count += 1
            #     continue
            if journal_name.lower() in journals:
                count += 1
                self.logger.info(f'Journal existed {journal_name}')
                continue
            self.logger.info(f'Current count: {count}')
            url = 'http://www.letpub.com.cn/index.php?page=journalapp&view=search'
            data = {
                'searchname': journal_name,
                'searchsort': 'relevance'
            }
            yield FormRequest(url, callback=self.parse, formdata=data, meta={'if': impact_factor, 'name': journal_name, 'depth': 0})
            count += 1

    def parse(self, response):
        name = response.request.meta['name']
        depth = response.request.meta['depth']
        impact_factor = response.request.meta['if']
        soup =  BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table',{"class":"table_yjfx"})
        if table is None:
            self.logger.warning(f'[ERR:0] Failed to retrieve journal: {name}.')
            if depth > 5:
                return
            self.logger.info(f'Try again to retrieve journal: {name}...')
            url = 'http://www.letpub.com.cn/index.php?page=journalapp&view=search'
            data = {
                'searchname': name,
                'searchsort': 'relevance'
            }
            depth += 1
            yield FormRequest(url, callback=self.parse, formdata=data, meta={'if': impact_factor, 'name': name, 'depth': depth})
            return
        trs = list(table.find_all('tr'))
        if len(trs) < 4:
            self.logger.warning(f'[ERR:1] Failed to retrieve journal: {name}.')
            return
        tr = trs[2]
        href = list(tr.find_all('td'))[1].find('a')['href']
        yield DetailUrl(name=name, impact_factor=impact_factor, href=href)
        # self.logger.info(f"User-Agent: {response.request.headers['User-Agent']}")
        self.logger.info(f'Succeed to parse detail url of {name}: {href}.')

    def parse_detail(self, response):
        name = response.request.meta['name']
        impact_factor = response.request.meta['if']
        soup =  BeautifulSoup(response.text, 'html.parser')
        anchor = soup.find('div', {'class': 'layui-row'})
        for _ in range(4):
            anchor = anchor.next_sibling

        table = anchor
        trs = list(table.find('tbody').children)
        idx = 2
        name_tr = trs[idx]
        idx += 1
        ssin_tr = trs[idx]
        idx += 1
        e_ssin_tr = trs[idx]
        if 'P-ISSN' in e_ssin_tr.text:
            e_ssin_tr = None
            idx += 1
        elif 'E-ISSN' not in e_ssin_tr.text:
            e_ssin_tr = None
        else:
            idx += 1

        self_cite_ratio_tr = trs[idx]
        idx += 2
        try:
            cite_score_table = trs[idx].find_all('tr')[1].find('table')
        except:
            cite_score_table = None

        in_messy = list(list(trs[-1].children)[1].children)
        try:
            cas_base_table = in_messy[2]
            cas_new_table = list(list(in_messy[3].children)[1].children)[0]
        except:
            cas_base_table = None
            cas_new_table = None

        name_span = name_tr.find('span')
        full_name = name_span.find('a').text
        abrv_name = name_span.find('font').text
        ssin = ssin_tr.find_all('td')[1].text
        e_ssin = ""
        if e_ssin_tr is not None:
            e_ssin = e_ssin_tr.find_all('td')[1].text

        try:
            self_cite_ratio = round(float(self_cite_ratio_tr.find_all('td')[1].text.split('%')[0]) / 100, 4)
        except:
            self_cite_ratio = -1

        if cite_score_table is not None:
            jcr_trs = cite_score_table.find_all('tr')[1:]
            jcr_cat_code = None
            jcr_sub = []
            for jcr_tr in jcr_trs:
                jcr_tds = jcr_tr.find_all('td')
                cat_name = jcr_tds[0].text[3:]
                cat, sub_cat = cat_name.split('小类：')
                code = jcr_tds[1].text
                if jcr_cat_code is None:
                    jcr_cat_code = [cat, code]
                jcr_sub.append(sub_cat)
        else:
            jcr_sub = []
            jcr_cat_code = [None, None]

        if cas_base_table is not None:
            cas_base_tds = list(cas_base_table.children)[1].find_all('td', recursive=False)
            cas_base_cat = cas_base_tds[0].contents[0].strip()
            cas_base_cat_code = cas_base_tds[0].find('span', style=lambda value: value and 'display:none' not in value).text
            cas_base_sub = []
            for tr in cas_base_tds[1].table.children:
                tds = tr.find_all('td')
                sub_en = tds[0].contents[0]
                sub = tds[0].contents[-1]
                sub_code = tds[1].find('span', style=lambda value: value and 'display:none' not in value).text
                cas_base_sub.append([sub, sub_en, sub_code])
            cas_base_top = cas_base_tds[2].text
            cas_base_review = cas_base_tds[3].text
        else:
            cas_base_cat = None
            cas_base_cat_code = None
            cas_base_sub = []
            cas_base_top = None
            cas_base_review = None

        if cas_new_table is not None:
            cas_new_tds = list(cas_new_table.children)[1].find_all('td', recursive=False)
            cas_new_cat = cas_new_tds[0].contents[0].strip()
            cas_new_cat_code = cas_new_tds[0].find('span', style=lambda value: value and 'display:none' not in value).text
            cas_new_sub = []
            for tr in cas_new_tds[1].table.children:
                tds = tr.find_all('td')
                sub_en = tds[0].contents[0]
                sub = tds[0].contents[-1]
                sub_code = tds[1].find('span', style=lambda value: value and 'display:none' not in value).text
                cas_new_sub.append([sub, sub_en, sub_code])
            cas_new_top = cas_new_tds[2].text
            cas_new_review = cas_new_tds[3].text
        else:
            cas_new_cat = None
            cas_new_cat_code = None
            cas_new_sub = []
            cas_new_top = None
            cas_new_review = None

        item = JournalItem(
            name=full_name,
            abrv_name=abrv_name,
            impact_factor=impact_factor,
            ssin=ssin,
            e_ssin=e_ssin,
            self_citation_ratio=self_cite_ratio,
            jcr_cat_code=jcr_cat_code,
            jcr_sub=jcr_sub,
            cas_base=[cas_base_cat, cas_base_cat_code],
            cas_base_sub=cas_base_sub,
            cas_base_top=cas_base_top,
            cas_base_review=cas_base_review,
            cas_new=[cas_new_cat, cas_new_cat_code],
            cas_new_sub=cas_new_sub,
            cas_new_top=cas_new_top,
            cas_new_review=cas_new_review,
        )
        yield item
        self.logger.debug(f'{full_name} {name}')
        # self.logger.debug(f'Yield {item}')

        # self.logger.info(f"User-Agent: {response.request.headers['User-Agent']}")
        self.logger.info(f'Succeed in parse_detail for {full_name}.')

