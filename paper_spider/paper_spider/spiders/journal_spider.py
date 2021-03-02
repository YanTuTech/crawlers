import scrapy
import json
from bs4 import BeautifulSoup
from paper_spider.items import *
from utils import *
from scrapy.http.request.form import FormRequest

class JournalsSpider(scrapy.Spider):
    name = "journals"

    def start_requests(self):
        journal_gen = get_journals()
        
        count = 0
        for journal_name, impact_factor in journal_gen:
            if count > 3:
                break
            url = 'http://www.letpub.com.cn/index.php?page=journalapp&view=search'
            data = {
                'searchname': journal_name
            }
            yield FormRequest(url, callback=self.parse, formdata=data, meta={'if': impact_factor, 'name': journal_name})
            count += 1

    def parse(self, response):
        name = response.request.meta['name']
        impact_factor = response.request.meta['if']
        soup =  BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table',{"class":"table_yjfx"})
        if table is None:
            self.logger.warning(f'[ERR:0] Failed to retrieve journal: {name}.')
            return
        trs = list(table.find_all('tr'))
        if len(trs) < 4:
            self.logger.warning(f'[ERR:1] Failed to retrieve journal: {name}.')
            return
        tr = trs[2]
        href = list(tr.find_all('td'))[1].find('a')['href']
        yield DetailUrl(name=name, impact_factor=impact_factor, href=href)
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
        if 'E-ISSN' not in e_ssin_tr.text:
            e_ssin_tr = None
        else:
            idx += 1
        self_cite_ratio_tr = trs[idx]
        idx += 2
        cite_score_table = trs[idx].find_all('tr')[1].find('table')

        in_messy = list(list(trs[-1].children)[1].children)
        cas_base_table = in_messy[2]
        cas_new_table = list(list(in_messy[3].children)[1].children)[0]

        name_span = name_tr.find('span')
        full_name = name_span.find('a').text
        abrv_name = name_span.find('font').text
        ssin = ssin_tr.find_all('td')[1].text
        e_ssin = ""
        if e_ssin_tr is not None:
            e_ssin = e_ssin_tr.find_all('td')[1].text
        self_cite_ratio = round(float(self_cite_ratio_tr.find_all('td')[1].text.split('%')[0]) / 100, 4)

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
        # self.logger.info([cas_base_cat, cas_base_cat_code])
        # self.logger.info(cas_base_sub)
        # self.logger.info(cas_base_top)
        # self.logger.info(cas_base_review)
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
        # self.logger.info([cas_new_cat, cas_new_cat_code])
        # self.logger.info(cas_new_sub)
        # self.logger.info(cas_new_top)
        # self.logger.info(cas_new_review)
        item = Journal(
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

        # self.logger.info(f'{full_name}, {abrv_name}, {ssin}, {e_ssin}, {self_cite_ratio}')
        self.logger.info(f'Succeed in parse_detail for {full_name}.')

