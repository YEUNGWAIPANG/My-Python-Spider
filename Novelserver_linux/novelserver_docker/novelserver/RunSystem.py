import os
import sqlite3
import yagmail
import datetime
import requests
from time import sleep
from lxml import etree
from faker import Faker
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

def writeRunLogFile(info:str):
    def gettime():
        ctime=datetime.datetime.now()
        day=ctime.strftime("%Y.%m.%d ")
        hms=ctime.strftime("%H%M%S")

        HMS=str(hms)
        hour=HMS[0:2]
        minute=HMS[2:4]
        second=HMS[4:6]
        nowtime=day+hour+":"+minute+":"+second
        return str(nowtime)

    file = open("./configfiles/runlog.log","a",encoding='utf-8')
    file.write(gettime() + "    " + info + "\n")
    file.close()

class config:
    def __init__(self) -> None:
        if not os.path.exists("./book"):
            os.mkdir("./book")
        if not os.path.exists("./configfiles"):
            os.mkdir("./configfiles")
        try:
            self.configfile = open("./configfiles/taskurls.txt","r",encoding='utf-8')
        except FileNotFoundError:
            self.configfile = open("./configfiles/taskurls.txt","w",encoding='utf-8')
            self.configfile.close()
            self.configfile = open("./configfiles/taskurls.txt","r",encoding='utf-8')
        # 检查本地有没有数据库文件，没有就创建，有数据库文件但没有表就创建表
        if not os.path.exists("./configfiles/taskdata.db"):
            self.db = sqlite3.connect("./configfiles/taskdata.db")
            self.db.cursor().execute("""
            CREATE TABLE linkstable(
                bookname TEXT NOT NULL UNIQUE,  
                link TEXT NOT NULL UNIQUE
            )
            """)
            self.db.commit()
        else:
            self.db = sqlite3.connect("./configfiles/taskdata.db")
            try:
                # 如果报错就证明有数据库但没有表
                self.db.cursor().execute("SELECT * FROM linkstable")
            except sqlite3.OperationalError:
                self.db.cursor().execute("""
                CREATE TABLE linkstable(
                    bookname TEXT NOT NULL UNIQUE,
                    link TEXT NOT NULL UNIQUE
                )
                """)
                self.db.commit()
        
    def searchbook(self,booklink):
        try:
            r = requests.get(booklink,headers={"User-Agent":Faker().user_agent()})
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            r = etree.HTML(r.text)
            bookname = r.xpath('//div[@class="info"]/div/h1/text()')[0]
            result = True
        except:
            bookname = ""
            result = False
        if result == True:
            self.db.cursor().execute("INSERT INTO linkstable VALUES('%s','%s')"%(bookname,booklink))
            self.db.cursor().execute("""
                CREATE TABLE '%s'(
                    sectionID INT UNIQUE NOT NULL,
                    sectionLink TEXT UNIQUE NOT NULL,
                    statuscode INT CHECK(statuscode = 0 OR statuscode = 1) NOT NULL
                )
            """%bookname)
            self.db.commit()
        else:
            info = 'Error:"' + booklink + '"' + "非小说源的小说首页或服务器拒绝了访问。"
            writeRunLogFile(info)

    def run(self) -> None:
        taskurls = []
        for url in self.configfile.readlines():
            taskurls.append(url.replace("\n",""))
        for booklink in taskurls:
            cur = self.db.cursor()
            cur.execute("SELECT * FROM linkstable WHERE link = '%s'"%booklink)
            if len(cur.fetchall())  == 0 :
                self.searchbook(booklink)
            else:
                continue
        cur = self.db.cursor()
        cur.execute("SELECT link FROM linkstable")
        databaseBooklinks = cur.fetchall()
        for databaseBooklink in databaseBooklinks:
            if databaseBooklink[0] not in taskurls:
                cur = self.db.cursor()
                cur.execute("SELECT bookname FROM linkstable WHERE link = '%s'"%databaseBooklink[0])
                bookname = cur.fetchall()[0][0]
                self.db.cursor().execute("DROP TABLE '%s'"%bookname)
                self.db.commit()
                self.db.cursor().execute("DELETE FROM linkstable WHERE link = '%s'"%databaseBooklink[0])
                self.db.commit()
        self.configfile.close()

class spider:
    def __init__(self,bookname,link) -> None:
        self.bookname = bookname
        self.link = link
        self.db = sqlite3.connect("./configfiles/taskdata.db")
        self.lock = Lock()
        self.alldownloadedsection = {}

    def check(self):
        r = requests.get(self.link,headers={"User-Agent":Faker().user_agent()})
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        r = etree.HTML(r.text)
        sectionlist = []
        sectionlinklist = r.xpath('//div[@class="section-box"][2]/ul[@class="section-list fix"]/li/a/@href')
        for sectionlink in sectionlinklist:
            sectionlist.append((sectionlinklist.index(sectionlink)+1,self.link+sectionlink))
        localsectionlist = self.db.cursor().execute("SELECT sectionID,sectionLink FROM '%s'"%self.bookname).fetchall()
        for section in sectionlist:
            if section not in localsectionlist:
                self.db.cursor().execute("INSERT INTO '%s' VALUES ('%d','%s',0)"%(self.bookname,section[0],section[1]))
        self.db.commit()

    def download(self,sectionID,sectionlink):
        print("正在下载:《" + self.bookname + "》第" + str(sectionID) + "章,链接为:" + sectionlink)
        allcontent = []
        while True:
            try:
                r = requests.get(sectionlink,headers={"User-Agent":Faker().user_agent()})
                if r.status_code == 200:
                    break
            except:
                sleep(2)
                continue
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        tree = etree.HTML(r.text)
        title = tree.xpath('//h1[@class="title"]/text()')[0]
        allcontent.append(title)
        contents = tree.xpath('//div[@id="content"]/text()')
        for content in contents:
            contents[contents.index(content)].strip()
            contents[contents.index(content)] = "".join(contents[contents.index(content)].split())
        for content in contents:
            if content != "":
                allcontent.append("    " + content)
        while True:
            nextpartlink_node = tree.xpath('//a[text()="下一页"]')
            if len(nextpartlink_node) != 0:
                nextpartlink = tree.xpath('//a[text()="下一页"]/@href')[0]
                r = requests.get("http://www.ywggzy.com" + nextpartlink,headers={"User-Agent":Faker().user_agent()})
                r.raise_for_status()
                tree = etree.HTML(r.text)
                contents = tree.xpath('//div[@id="content"]/text()')
                for content in contents:
                    contents[contents.index(content)].strip()
                    contents[contents.index(content)] = "".join(contents[contents.index(content)].split())
                for content in contents:
                    if content != "":
                        allcontent.append("    " + content)
            else:
                break
        sectioncontent = "\n".join(allcontent)
        self.lock.acquire()
        self.alldownloadedsection[sectionID] = sectioncontent
        writeRunLogFile(self.bookname + "第" + str(sectionID) + "章(链接:" + sectionlink + ")下载成功。")
        self.lock.release()
        sleep(2)

    def send(self,sectionID,content):
        subject = "《" + self.bookname + "》  第" + str(sectionID) +"章"
        qq = yagmail.SMTP(user="2946706968@qq.com",password="xvuhotgrmfocdgae",host="smtp.qq.com",smtp_ssl = True)
        qq.send(to="2946706968@qq.com",subject=subject,contents=content)

    def save(self):
        self.alldownloadedsection = sorted(self.alldownloadedsection.items(),key=lambda item:item[0]) # 返回一个元组，元组里面又是每个章节的元组
        with open("./book/" + self.bookname + ".txt","a+",encoding="utf-8") as f:
            for i in self.alldownloadedsection:
                f.write(i[1])
                f.write("\n")
        for section in self.alldownloadedsection:
            self.db.cursor().execute("UPDATE '%s' SET statuscode = '%d' WHERE sectionID = '%d'"%(self.bookname,1,section[0]))
        self.db.commit()
        if len(self.alldownloadedsection) > 3:
            needsend = self.alldownloadedsection[-3:]
            for sended in needsend:
                self.send(sended[0],sended[1])
        else:
            for sended in self.alldownloadedsection:
                self.send(sended[0],sended[1])

    def run(self):
        self.check()
        cur = self.db.cursor()
        allneeddownload = cur.execute("SELECT sectionID,sectionLink From '%s' WHERE statuscode = 0"%self.bookname).fetchall()
        pool = ThreadPoolExecutor(15)
        for book in allneeddownload:
            pool.submit(self.download,book[0],book[1])
        pool.shutdown()
        self.save()

if __name__ == "__main__":
    config().run()
    db = sqlite3.connect("./configfiles/taskdata.db")
    tasks = db.cursor().execute("SELECT * FROM linkstable").fetchall()
    db.close()
    for task in tasks:
        spider(task[0],task[1]).run()
