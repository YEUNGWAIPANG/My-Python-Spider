# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymysql
from .settings import nowtime,MySQL_host,MySQL_port,MySQL_user,MySQL_password,MySQL_database
from .items import DangdangChangxiaobangItem,DangdangXinshuremaibangItem,DangdangHaopingbangItem

class DangdangChangxiaobangPipeline: 
    def __init__(self) -> None:
        self.tablename = '24小时畅销榜TOP500' + nowtime
        try:
            self.db = pymysql.connect(host=MySQL_host,port=MySQL_port,user=MySQL_user,password=MySQL_password,database=MySQL_database)
        except pymysql.err.OperationalError:
            db = pymysql.connect(host=MySQL_host,port=MySQL_port,user=MySQL_user,password=MySQL_password)
            cur = db.cursor()
            cur.execute("CREATE DATABASE %s;"%MySQL_database)
            db.commit()
            db.close()
            self.db = pymysql.connect(host=MySQL_host,port=MySQL_port,user=MySQL_user,password=MySQL_password,database=MySQL_database)

    def open_spider(self, spider):
        cur = self.db.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS %s(
                书名 TEXT NOT NULL,
                作者 TEXT NOT NULL,
                出版社 TEXT NOT NULL,
                原价 FLOAT NOT NULL,
                现价 FLOAT NOT NULL,
                折扣 FLOAT NOT NULL,
                好评率 FLOAT NOT NULL,
                链接 TEXT NOT NULL
            )
        """%self.tablename)
        self.db.commit()

    def process_item(self, item, spider):
        if isinstance(item,DangdangChangxiaobangItem):
            self.db.cursor().execute("INSERT INTO %s VALUES('%s','%s','%s','%s','%s','%s','%s','%s')"%(self.tablename,item['bookname'],item['writer'],item['press'],item['preprice'],item['nowprice'],item['discount'],item['goodcomment_persent'],item['link']))
            self.db.commit()
        return item

    def close_spider(self, spider):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM %s"%self.tablename)
        if len(cur.fetchall()) == 0:
            self.db.cursor().execute("DROP TABLE IF EXISTS %s"%self.tablename)
            self.db.commit()
        self.db.close()

class DangdangXinshuremaibangPipeline: 
    def __init__(self) -> None:
        self.tablename = '24小时新书热卖榜TOP500' + nowtime
        try:
            self.db = pymysql.connect(host=MySQL_host,port=MySQL_port,user=MySQL_user,password=MySQL_password,database=MySQL_database)
        except pymysql.err.OperationalError:
            db = pymysql.connect(host=MySQL_host,port=MySQL_port,user=MySQL_user,password=MySQL_password)
            cur = db.cursor()
            cur.execute("CREATE DATABASE %s;"%MySQL_database)
            db.commit()
            db.close()
            self.db = pymysql.connect(host=MySQL_host,port=MySQL_port,user=MySQL_user,password=MySQL_password,database=MySQL_database)

    def open_spider(self, spider):
        cur = self.db.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS %s(
                书名 TEXT NOT NULL,
                作者 TEXT NOT NULL,
                出版社 TEXT NOT NULL,
                原价 FLOAT NOT NULL,
                现价 FLOAT NOT NULL,
                折扣 FLOAT NOT NULL,
                好评率 FLOAT NOT NULL,
                链接 TEXT NOT NULL
            )
        """%self.tablename)
        self.db.commit()

    def process_item(self, item, spider):
        if isinstance(item,DangdangXinshuremaibangItem):
            self.db.cursor().execute("INSERT INTO %s VALUES('%s','%s','%s','%s','%s','%s','%s','%s')"%(self.tablename,item['bookname'],item['writer'],item['press'],item['preprice'],item['nowprice'],item['discount'],item['goodcomment_persent'],item['link']))
            self.db.commit()
        return item

    def close_spider(self, spider):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM %s"%self.tablename)
        if len(cur.fetchall()) == 0:
            self.db.cursor().execute("DROP TABLE IF EXISTS %s"%self.tablename)
            self.db.commit()
        self.db.close()

class DangdangHaopingbangPipeline: 
    def __init__(self) -> None:
        self.tablename = '近30天好评榜TOP500' + nowtime
        try:
            self.db = pymysql.connect(host=MySQL_host,port=MySQL_port,user=MySQL_user,password=MySQL_password,database=MySQL_database)
        except pymysql.err.OperationalError:
            db = pymysql.connect(host=MySQL_host,port=MySQL_port,user=MySQL_user,password=MySQL_password)
            cur = db.cursor()
            cur.execute("CREATE DATABASE %s;"%MySQL_database)
            db.commit()
            db.close()
            self.db = pymysql.connect(host=MySQL_host,port=MySQL_port,user=MySQL_user,password=MySQL_password,database=MySQL_database)

    def open_spider(self, spider):
        cur = self.db.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS %s(
                书名 TEXT NOT NULL,
                作者 TEXT NOT NULL,
                出版社 TEXT NOT NULL,
                原价 FLOAT NOT NULL,
                现价 FLOAT NOT NULL,
                折扣 FLOAT NOT NULL,
                好评率 FLOAT NOT NULL,
                链接 TEXT NOT NULL
            )
        """%self.tablename)
        self.db.commit()

    def process_item(self, item, spider):
        if isinstance(item,DangdangHaopingbangItem):
            self.db.cursor().execute("INSERT INTO %s VALUES('%s','%s','%s','%s','%s','%s','%s','%s')"%(self.tablename,item['bookname'],item['writer'],item['press'],item['preprice'],item['nowprice'],item['discount'],item['goodcomment_persent'],item['link']))
            self.db.commit()
        return item

    def close_spider(self, spider):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM %s"%self.tablename)
        if len(cur.fetchall()) == 0:
            self.db.cursor().execute("DROP TABLE IF EXISTS %s"%self.tablename)
            self.db.commit()
        self.db.close()
