# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class DangdangChangxiaobangItem(scrapy.Item):
    bookname = scrapy.Field()
    writer = scrapy.Field()
    press = scrapy.Field()
    preprice = scrapy.Field()
    nowprice = scrapy.Field()
    discount = scrapy.Field()
    goodcomment_persent = scrapy.Field()
    link = scrapy.Field()

class DangdangXinshuremaibangItem(scrapy.Item):
    bookname = scrapy.Field()
    writer = scrapy.Field()
    press = scrapy.Field()
    preprice = scrapy.Field()
    nowprice = scrapy.Field()
    discount = scrapy.Field()
    goodcomment_persent = scrapy.Field()
    link = scrapy.Field()

class DangdangHaopingbangItem(scrapy.Item):
    bookname = scrapy.Field()
    writer = scrapy.Field()
    press = scrapy.Field()
    preprice = scrapy.Field()
    nowprice = scrapy.Field()
    discount = scrapy.Field()
    goodcomment_persent = scrapy.Field()
    link = scrapy.Field()
