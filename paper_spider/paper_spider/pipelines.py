# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from paper_spider.items import Journal as JournalItem
from db import *
import logging 
logger = logging.getLogger(__name__)


class PaperSpiderPipeline:
    def process_item(self, item, spider):
        if type(item) is not JournalItem:
            return item
        if Journal.select().where(Journal.name==item['name']).exists():
            logger.info(f'Journal {item["name"]} existed.')
            return item
        journal = Journal.create(
            name=item['name'],
            abrv_name=item['abrv_name'],
            impact_factor=item['impact_factor'],
            ssin=item['ssin'],
            e_ssin=item['e_ssin'],
            self_citation_ratio=item['self_citation_ratio'],
            cas_base_top=True if item['cas_base_top'] == "是" else False,
            cas_base_review=True if item['cas_base_review'] == "是" else False,
            cas_new_top=True if item['cas_new_top'] == "是" else False,
            cas_new_review=True if item['cas_new_review'] == "是" else False,
        )

        jcr_cat_query = JCRCategory.select().where(JCRCategory.name==item['jcr_cat_code'][0])
        jcr_cat = None
        if not jcr_cat_query.exists():
            jcr_cat = JCRCategory.create(name=item['jcr_cat_code'][0], code=item['jcr_cat_code'][1])
            # logger.info(f'JCRCat {item["jcr_cat_code"][1]} created.')
        else:
            jcr_cat = jcr_cat_query.first()
            # logger.info(f'JCRCat {item["jcr_cat_code"][1]} existed.')
        journal.jcr_cat = jcr_cat

        cas_base_query = CASBaseCategory.select().where(CASBaseCategory.name==item['cas_base'][0])
        cas_base = None
        if not cas_base_query.exists():
            cas_base = CASBaseCategory.create(name=item['cas_base'][0], code=item['cas_base'][1])
            # logger.info(f'BaseCat {item["cas_base"][0]} created.')
        else:
            cas_base =cas_base_query.first()
            # logger.info(f'BaseCat {item["cas_base"][0]} existed.')
        journal.cas_base = cas_base

        cas_new_query = CASNewCategory.select().where(CASNewCategory.name==item['cas_new'][0])
        cas_new = None
        if not cas_new_query.exists():
            cas_new = CASNewCategory.create(name=item['cas_new'][0], code=item['cas_new'][1])
            # logger.info(f'NewCat {item["cas_new"][0]} created.')
        else:
            cas_new =cas_new_query.first()
            # logger.info(f'NewCat {item["cas_new"][0]} existed.')
        journal.cas_new = cas_new

        for sub in item['jcr_sub']:
            sub_instance = None
            sub_query = JCRSubCategory.select().where(JCRSubCategory.name==sub)
            if sub_query.exists():
                sub_instance = sub_query.first()
                # logger.info(f'JCRSubCat {sub} existed.')
            else:
                sub_instance = JCRSubCategory.create(name=sub)
                # logger.info(f'JCRSubCat {sub} created.')
            JCRSubCatRel.create(sub_cat=sub_instance, journal=journal)
        
        for sub in item['cas_base_sub']:
            sub_instance = None
            sub_query = CASBaseSubCategory.select().where(CASBaseSubCategory.name==sub[0])
            if sub_query.exists():
                sub_instance = sub_query.first()
                # logger.info(f'BaseSubCat {sub[0]} existed.')
            else:
                sub_instance = CASBaseSubCategory.create(name=sub[0], en_name=sub[1], code=sub[2])
                # logger.info(f'BaseSubCat {sub[0]} created.')
            CASBaseSubCatRel.create(cas_base_sub=sub_instance, journal=journal)
        
        for sub in item['cas_new_sub']:
            sub_instance = None
            sub_query = CASNewSubCategory.select().where(CASNewSubCategory.name==sub[0])
            if sub_query.exists():
                sub_instance = sub_query.first()
                # logger.info(f'NewSubCat {sub[0]} existed.')
            else:
                sub_instance = CASNewSubCategory.create(name=sub[0], en_name=sub[1], code=sub[2])
                # logger.info(f'NewSubCat {sub[0]} created.')
            CASNewSubCatRel.create(cas_new_sub=sub_instance, journal=journal)
        
        journal.save()
        logger.info(f'Journal {item["name"]} created.')
        return item
