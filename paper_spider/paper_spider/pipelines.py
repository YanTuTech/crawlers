# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from paper_spider.items import *

class PaperSpiderPipeline:
    def process_item(self, item, spider):
        if type(item) is not Journal:
            return item
        # store journal
        return item
