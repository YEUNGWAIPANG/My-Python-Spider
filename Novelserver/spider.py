import os
import sqlite3
import yagmail
import requests
from time import sleep
from lxml import etree
from threading import Lock
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor

class spider:
    def __init__(self,bookname,link) -> None:
        self.bookname = bookname
        self.link = link
        self.db = sqlite3.connect("taskdata.db")
        self.lock = Lock()
        self.alldownloadedsection = {}

    def check(self):
        r = requests.get(self.link,headers={"User-Agent":UserAgent(path="fake_useragent_0.1.11.json").random})
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
                r = requests.get(sectionlink,headers={"User-Agent":UserAgent(path="./fake_useragent_0.1.11.json").random})
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
                r = requests.get("http://www.ywggzy.com" + nextpartlink,headers={"User-Agent":UserAgent(path="./fake_useragent_0.1.11.json").random})
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
        # sqlite不支持同一个连接对象被多个线程使用，所以这里为每个线程创建一个临时连接，同时加锁，确保同时只有一个线程创建了连接。
        with sqlite3.connect("taskdata.db") as conn:
            conn.execute("UPDATE '%s' SET statuscode = '%d' WHERE sectionID = '%d'"%(self.bookname,1,sectionID))
            conn.commit()
        self.alldownloadedsection[sectionID] = sectioncontent
        self.lock.release()

    def send(self,sectionID,content):
        subject = "《" + self.bookname + "》  第" + str(sectionID) +"章"
	# user填写自己的邮箱,password填写自己的邮箱的授权码，授权码获取自行参考各个邮箱，host填写所用邮箱服务器host(如qq邮箱的smtp.qq.com)
        email = yagmail.SMTP(user="",password="",host="",smtp_ssl = True)
	# to：接收的邮箱。可以与发送邮箱一样。
        email.send(to="",subject=subject,contents=content)

    def save(self):
        self.alldownloadedsection = sorted(self.alldownloadedsection.items(),key=lambda item:item[0]) # 返回一个元组，元组里面又是每个章节的元组
        with open("./book/" + self.bookname + ".txt","a+",encoding="utf-8") as f:
            for i in self.alldownloadedsection:
                f.write(i[1])
                f.write("\n")
        if len(self.alldownloadedsection) > 3:
            needsend = self.alldownloadedsection[-3:]
            for sended in needsend:
                self.send(sended[0],sended[1])
        else:
            for sended in self.alldownloadedsection:
                self.send(sended[0],sended[1])

    def run(self):
        self.check()
        allneeddownload = self.db.cursor().execute("SELECT sectionID,sectionLink From '%s' WHERE statuscode = 0"%self.bookname).fetchall()
        pool = ThreadPoolExecutor(15)
        for book in allneeddownload:
            pool.submit(self.download,book[0],book[1])
        pool.shutdown()
        self.save()
	self.db.close()

if __name__ == "__main__":
    if os.path.exists("taskdata.db"):
        db = sqlite3.connect("taskdata.db")
        tasks = db.cursor().execute("SELECT * FROM linkstable").fetchall()
        db.close()
        for task in tasks:
            spider(task[0],task[1]).run()
    else:
        print("\n本地未找到数据库文件,说明您还未配置config,请先在config.exe中进行应用初始化及配置。\n")
