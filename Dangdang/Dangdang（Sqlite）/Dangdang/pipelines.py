# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import sqlite3
from .Gettime import gettime
from .items import DangdangChangxiaobangItem,DangdangXinshuremaibangItem,DangdangHaopingbangItem

nowtime = gettime()
class DangdangChangxiaobangPipeline(object):
    def __init__(self) -> None:
        if not os.path.exists("./Data"):
            os.mkdir("./Data")
        self.db = sqlite3.connect("./Data/Dangdang" + nowtime +".db")

    def open_spider(self, spider):
        try:
            self.db.execute("SELECT * FROM '24小时畅销榜TOP500'").fetchall()
        except:
            self.db.cursor().execute("""
                CREATE TABLE '24小时畅销榜TOP500'(
                    书名 TEXT NOT NULL,
                    作者 TEXT NOT NULL,
                    出版社 TEXT NOT NULL,
                    原价 FLOAT NOT NULL,
                    现价 FLOAT NOT NULL,
                    折扣 FLOAT NOT NULL,
                    好评率 FLOAT NOT NULL,
                    链接 TEXT NOT NULL
                )
            """)
            self.db.commit()

    def process_item(self, item, spider):
        if isinstance(item,DangdangChangxiaobangItem):
            self.db.execute("INSERT INTO '24小时畅销榜TOP500' VALUES('%s','%s','%s','%s','%s','%s','%s','%s')"%(item['bookname'],item['writer'],item['press'],item['preprice'],item['nowprice'],item['discount'],item['goodcomment_persent'],item['link']))
            self.db.commit()
        return item

    def close_spider(self, spider):
        self.db.close()

class DangdangXinshuremaibangPipeline(object):
    def __init__(self) -> None:
        if not os.path.exists("./Data"):
            os.mkdir("./Data")
        self.db = sqlite3.connect("./Data/Dangdang" + nowtime +".db")

    def open_spider(self, spider):
        try:
            self.db.execute("SELECT * FROM '24小时新书热卖榜TOP500'").fetchall()
        except:
            self.db.cursor().execute("""
                CREATE TABLE '24小时新书热卖榜TOP500'(
                    书名 TEXT NOT NULL,
                    作者 TEXT NOT NULL,
                    出版社 TEXT NOT NULL,
                    原价 FLOAT NOT NULL,
                    现价 FLOAT NOT NULL,
                    折扣 FLOAT NOT NULL,
                    好评率 FLOAT NOT NULL,
                    链接 TEXT NOT NULL
                )
            """)
            self.db.commit()

    def process_item(self, item, spider):
        if isinstance(item,DangdangXinshuremaibangItem):
            self.db.execute("INSERT INTO '24小时新书热卖榜TOP500' VALUES('%s','%s','%s','%s','%s','%s','%s','%s')"%(item['bookname'],item['writer'],item['press'],item['preprice'],item['nowprice'],item['discount'],item['goodcomment_persent'],item['link']))
            self.db.commit()
        return item

    def close_spider(self, spider):
        self.db.close()

class DangdangHaopingbangPipeline(object):
    def __init__(self) -> None:
        if not os.path.exists("./Data"):
            os.mkdir("./Data")
        self.db = sqlite3.connect("./Data/Dangdang" + nowtime +".db")

    def open_spider(self, spider):
        try:
            self.db.execute("SELECT * FROM '近30天好评榜TOP500'").fetchall()
        except:
            self.db.cursor().execute("""
                CREATE TABLE '近30天好评榜TOP500'(
                    书名 TEXT NOT NULL,
                    作者 TEXT NOT NULL,
                    出版社 TEXT NOT NULL,
                    原价 FLOAT NOT NULL,
                    现价 FLOAT NOT NULL,
                    折扣 FLOAT NOT NULL,
                    好评率 FLOAT NOT NULL,
                    链接 TEXT NOT NULL
                )
            """)
            self.db.commit()

    def process_item(self, item, spider):
        if isinstance(item,DangdangHaopingbangItem):
            self.db.execute("INSERT INTO '近30天好评榜TOP500' VALUES('%s','%s','%s','%s','%s','%s','%s','%s')"%(item['bookname'],item['writer'],item['press'],item['preprice'],item['nowprice'],item['discount'],item['goodcomment_persent'],item['link']))
            self.db.commit()
        return item

    def close_spider(self, spider):
        self.db.close()
