# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import sqlite3
from Gettime import gettime
from .items import DoubanMovieItem,DoubanMusicItem,DoubanbookItem

nowtime = gettime()

class DoubanMoviePipeline(object):
    def __init__(self) -> None:
        if not os.path.exists("./Data"):
            os.mkdir("./Data")
        self.db = sqlite3.connect("./Data/DoubanTop250" + nowtime  +".db")

    def open_spider(self, spider) -> None:
        self.db.cursor().execute("""
            CREATE TABLE movie(
                电影名 TEXT NOT NULL UNIQUE,
                电影类型 TEXT NOT NULL,
                上映时间 INT NOT NULL,
                国家 TEXT NOT NULL,
                评分 INT NOT NULL,
                评论人数 INT NOT NULL,
                工作人员 TEXT NOT NULL,
                描述 TEXT NOT NULL
                )
            """)
        self.db.commit()
        
    def process_item(self, item, spider):
        if isinstance(item,DoubanMovieItem):
            self.db.cursor().execute("INSERT INTO movie VALUES('%s','%s','%s','%s','%s','%s','%s','%s')"%(item['name'],item['movie_type'],item['time'],item['country'],item['rating'],item['comment'],item['worker'],item['describe']))
            self.db.commit()
        return item

    def close_spider(self, spider):
        self.db.close()

class DoubanMusicPipeline(object):
    def __init__(self) -> None:
        if not os.path.exists("./Data"):
            os.mkdir("./Data")
        self.db = sqlite3.connect("./Data/DoubanTop250" + nowtime  +".db")

    def open_spider(self, spider) -> None:
        self.db.cursor().execute("""
            CREATE TABLE music(
                歌曲名 TEXT NOT NULL UNIQUE,
                歌手 TEXT NOT NULL,
                发布时间 INT NOT NULL,
                类型 TEXT NOT NULL,
                风格 TEXT NOT NULL,
                评分 INT NOT NULL,
                评论人数 INT NOT NULL
                )
            """)
        self.db.commit()
        
    def process_item(self, item, spider):
        if isinstance(item,DoubanMusicItem):
            self.db.cursor().execute("INSERT INTO music VALUES('%s','%s','%s','%s','%s','%s','%s')"%(item['name'],item['singer'],item['time'],item['special'],item['style'],item['rating'],item['comment']))
            self.db.commit()
        return item

    def close_spider(self, spider):
        self.db.close()

class DoubanBookPipeline(object):
    def __init__(self) -> None:
        if not os.path.exists("./Data"):
            os.mkdir("./Data")
        self.db = sqlite3.connect("./Data/DoubanTop250" + nowtime  +".db")

    def open_spider(self, spider) -> None:
        self.db.cursor().execute("""
            CREATE TABLE book(
                书名 TEXT NOT NULL UNIQUE,
                作者 TEXT NOT NULL,
                译者 TEXT NOT NULL,
                出版社 TEXT NOT NULL,
                评分 INT NOT NULL,
                出版时间 TEXT NUT NULL,
                评论人数 INT NOT NULL,
                价格 INT NOT NULL
                )
            """)
        self.db.commit()
        
    def process_item(self, item, spider):
        if isinstance(item,DoubanbookItem):
            self.db.cursor().execute("INSERT INTO book VALUES('%s','%s','%s','%s','%s','%s','%s','%s')"%(item['bookname'],item['writer'],item['translator'],item['press'],item['rating'],item['time'],item['comment'],item['price']))
            self.db.commit()
        return item

    def close_spider(self, spider):
        self.db.close()
