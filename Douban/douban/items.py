# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class DoubanMovieItem(scrapy.Item):
    name = scrapy.Field() #
    worker = scrapy.Field() #
    time = scrapy.Field() #
    country = scrapy.Field() #
    movie_type = scrapy.Field() 
    rating = scrapy.Field() #
    comment = scrapy.Field()
    describe = scrapy.Field()

class DoubanMusicItem(scrapy.Item):
    name = scrapy.Field()
    singer = scrapy.Field()
    time = scrapy.Field()
    style = scrapy.Field()
    rating = scrapy.Field()
    comment = scrapy.Field()
    special = scrapy.Field()

class DoubanbookItem(scrapy.Item):
    bookname = scrapy.Field()
    writer = scrapy.Field()
    translator = scrapy.Field()
    press = scrapy.Field()
    time = scrapy.Field()
    rating = scrapy.Field()
    comment = scrapy.Field()
    price = scrapy.Field()
    