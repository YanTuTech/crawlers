# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class DetailUrl(scrapy.Item):
    name = scrapy.Field()
    impact_factor = scrapy.Field()
    href = scrapy.Field()

class Journal(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    abrv_name = scrapy.Field()
    impact_factor = scrapy.Field()
    ssin = scrapy.Field()
    e_ssin = scrapy.Field()
    self_citation_ratio = scrapy.Field()
    jcr_cat_code = scrapy.Field()
    jcr_sub = scrapy.Field()
    cas_base = scrapy.Field()
    cas_base_sub = scrapy.Field()
    cas_base_top = scrapy.Field()
    cas_base_review = scrapy.Field()
    cas_new = scrapy.Field()
    cas_new_sub = scrapy.Field()
    cas_new_top = scrapy.Field()
    cas_new_review = scrapy.Field()
