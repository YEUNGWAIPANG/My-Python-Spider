import os
import sys
import ctypes
import requests
from time import sleep
from lxml import etree
from threading import Lock
from fake_useragent import UserAgent
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread,pyqtSignal
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtWidgets import QMainWindow,QApplication,QMessageBox

# 发送搜索请求的线程
class SearchThread(QThread):
    signal = pyqtSignal(int,list)
    def __init__(self,searchtype,searchkey) -> None:
        super(SearchThread,self).__init__()
        self.searchtype = searchtype
        self.searchkey = searchkey
        self.status_code = None
        self.ResultList = []
    
    def run(self):
        Titles = []
        Writers = []
        Links = []
        data = {
            "searchkey": self.searchkey.encode("gbk"),
            "searchtype": self.searchtype,
            "page" : 1
        }
        try:
            r = requests.post("https://www.biqooge.com/modules/article/search.php",headers={"User-Agent":UserAgent(path="./resource/fake_useragent_0.1.11.json").random},data=data)
            r.raise_for_status()
            r.encoding = "gbk"
            if r.url != "https://www.biqooge.com/modules/article/search.php":
                Link = r.url
                r = etree.HTML(r.text)
                num = 1
                Title = r.xpath('//h1/text()')[0]
                Writer = r.xpath('//div[@id="info"]/p[1]/text()')[0].replace("作    者：","")
                self.ResultList.append((str(num),Title,Writer,Link))
                self.status_code = 1
            else:
                r = etree.HTML(r.text)
                lastpage = r.xpath('//a[@class="last"]/text()')
                if len(r.xpath('//table/tr[@id="nr"]')) == 0:
                    self.status_code = 0
                else:
                    self.status_code = 1
                    lastpage = int(lastpage[0])
                    title = r.xpath('//table/tr[@id="nr"]/td[1]/a/text()')
                    writer = r.xpath('//table/tr[@id="nr"]/td[3]/text()')
                    link = r.xpath('//table//tr[@id="nr"]/td[1]/a/@href')
                    Titles.extend(title)
                    Writers.extend(writer)
                    Links.extend(link)
                    for page in range(2,lastpage+1):
                        data = {
                            "searchkey": self.searchkey.encode("gbk"),
                            "searchtype": self.searchtype,
                            "page" : page
                        }
                        r = requests.post("https://www.biqooge.com/modules/article/search.php",headers={"User-Agent":UserAgent(path="./resource/fake_useragent_0.1.11.json").random},data=data)
                        r.raise_for_status()
                        r.encoding = "gbk"
                        r = etree.HTML(r.text)
                        title = r.xpath('//table/tr[@id="nr"]/td[1]/a/text()')
                        writer = r.xpath('//table/tr[@id="nr"]/td[3]/text()')
                        link = r.xpath('//table//tr[@id="nr"]/td[1]/a/@href')
                        Titles.extend(title)
                        Writers.extend(writer)
                        Links.extend(link)
                    num = 1
                    for Title,Writer,Link in zip(Titles,Writers,Links):
                        self.ResultList.append((str(num),Title,Writer,Link))
                        num += 1
        except requests.exceptions.HTTPError:
            self.status_code = -1
        self.signal.emit(self.status_code,self.ResultList)

# 下载小说的线程，用此线程管理多线程下载时的线程池UI不卡死。
class DownloadThread(QThread):
    fin_signal = QtCore.pyqtSignal(bool)
    content_signal = QtCore.pyqtSignal(str)
    total_signal = QtCore.pyqtSignal(int)

    def __init__(self,novelname,novellink,ThreadNum:int,saveplace):
        super(DownloadThread,self).__init__()
        self.novelname = novelname
        self.novellink = novellink
        self.AllSectionLink = []
        self.AllSection = {}
        self.result = False
        self.lock1 = Lock()
        self.lock2 = Lock()
        self.ThreadNum = ThreadNum
        self.saveplace = saveplace

    def __GetHtml(self,url):
        while True:
            try:
                r = requests.get(url,headers={"User-Agent":UserAgent(path="./resource/fake_useragent_0.1.11.json").random})
                if r.status_code == 200:
                    break
            except:
                sleep(2)
                continue
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text

    def run(self):
        def DownLoad(Section:tuple):
            Secnum = Section[0]
            Securl = Section[1]
            r = etree.HTML(self.__GetHtml(Securl))
            title = r.xpath('//div[@class="bookname"]/h1/text()')[0]
            contents = r.xpath('//div[@id="content"]/text()')
            for content in contents:
                contents[contents.index(content)] = "   " + content.replace("\n","").replace("&nbsp","").strip()
            content = title + "\n" + "\n".join(contents)
            self.lock1.acquire()
            self.AllSection[Secnum] = content
            self.lock1.release()
            self.content_signal.emit(content)
        try:
            r = etree.HTML(self.__GetHtml(self.novellink))
            AllSectionLink = r.xpath('//div[@id="list"]/dl/dt[2]/following::dd/a/@href')
            for link in AllSectionLink:
                self.AllSectionLink.append((AllSectionLink.index(link)+1,"https://www.biqooge.com" + link))
            # 总章节数通过信号发送给UI主线程用以设置进度条
            self.total_signal.emit(len(self.AllSectionLink))
            pool = ThreadPoolExecutor(self.ThreadNum)
            while len(self.AllSectionLink) != 0:
                self.lock2.acquire()
                Section = self.AllSectionLink.pop(0)
                self.lock2.release()
                pool.submit(DownLoad,Section)
            pool.shutdown()
            # 章节排序
            self.AllSection = sorted(self.AllSection.items(),key=lambda item:item[0])
            with open(self.saveplace + self.novelname + ".txt","w",encoding="utf-8") as f:
                for i in self.AllSection:
                    f.write(i[1])
                    f.write("\n")
            f.close()
            self.result = True
        except:
            pass
        self.fin_signal.emit(self.result)

# 主窗口
class Ui_MainWindow(object):
    def __init__(self):
        self.AllSection = {}
        self.AllSectionLink = []
        self.SearchThread = None
        self.DownloadThread = None
        self.novelurl =  None
        self.novelname = None
        if os.path.exists("Book") == False:
            os.makedirs("Book")

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1020, 835)
        MainWindow.setFixedSize(1020, 835)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
        MainWindow.setWindowIcon(QtGui.QIcon("./resource/Bookshelf.ico"))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(70, 350, 161, 41))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.DownloadNumEntry = QtWidgets.QLineEdit(self.layoutWidget)
        self.DownloadNumEntry.setObjectName("DownloadNumEntry")
        self.horizontalLayout_2.addWidget(self.DownloadNumEntry)
        self.Resulttable = QtWidgets.QTableWidget(self.centralwidget)
        self.Resulttable.setGeometry(QtCore.QRect(70, 80, 881, 261))
        self.Resulttable.setObjectName("Resulttable")
        self.Resulttable.setColumnCount(4)
        self.Resulttable.setRowCount(0)
        self.Resulttable.verticalHeader().setVisible(False)
        item = QtWidgets.QTableWidgetItem()
        self.Resulttable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.Resulttable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.Resulttable.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.Resulttable.setHorizontalHeaderItem(3, item)
        self.Resulttable.horizontalHeader().setStretchLastSection(True)
        self.Resulttable.verticalHeader().setCascadingSectionResizes(False)
        self.Resulttable.verticalHeader().setStretchLastSection(False)
    
        self.StartSearchButton = QtWidgets.QPushButton(self.centralwidget)
        self.StartSearchButton.setGeometry(QtCore.QRect(820, 30, 131, 34))
        self.StartSearchButton.setObjectName("StartSearchButton")
        self.StartSearchButton.clicked.connect(self.Search)
        self.Infotext = QtWidgets.QTextEdit(self.centralwidget)
        self.Infotext.setGeometry(QtCore.QRect(70, 430, 881, 371))
        self.Infotext.setObjectName("Infotext")
        self.Infotext.setReadOnly(True)
        self.DownloadButton = QtWidgets.QPushButton(self.centralwidget)
        self.DownloadButton.setGeometry(QtCore.QRect(770, 393, 181, 31))
        self.DownloadButton.setObjectName("DownloadButton")
        self.DownloadButton.clicked.connect(self.Download)
        self.layoutWidget1 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget1.setGeometry(QtCore.QRect(70, 30, 251, 31))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.layoutWidget1)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.SearchKeyEntry = QtWidgets.QLineEdit(self.layoutWidget1)
        self.SearchKeyEntry.setObjectName("SearchKeyEntry")
        self.horizontalLayout.addWidget(self.SearchKeyEntry)
        self.layoutWidget2 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget2.setGeometry(QtCore.QRect(400, 30, 341, 31))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.layoutWidget2)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.NovelnameradioButton = QtWidgets.QRadioButton(self.layoutWidget2)
        self.NovelnameradioButton.setObjectName("NovelnameradioButton")
        self.horizontalLayout_3.addWidget(self.NovelnameradioButton)
        self.WriterradioButton = QtWidgets.QRadioButton(self.layoutWidget2)
        self.WriterradioButton.setObjectName("WriterradioButton")
        self.horizontalLayout_3.addWidget(self.WriterradioButton)
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(70, 400, 81, 18))
        self.label_5.setObjectName("label_5")
        self.layoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget_2.setGeometry(QtCore.QRect(70, 380, 631, 51))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.layoutWidget_2)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_6 = QtWidgets.QLabel(self.layoutWidget_2)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_6.addWidget(self.label_6)
        self.SavePlaceEntry = QtWidgets.QLineEdit(self.layoutWidget_2)
        self.SavePlaceEntry.setObjectName("SavePlaceEntry")
        self.SavePlaceEntry.setPlaceholderText("若无指定则默认保存在当前目录Book文件夹下")
        self.horizontalLayout_6.addWidget(self.SavePlaceEntry)
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(620, 350, 341, 41))
        self.widget.setObjectName("widget")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_3 = QtWidgets.QLabel(self.widget)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)
        self.progressBar = QtWidgets.QProgressBar(self.widget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.horizontalLayout_4.addWidget(self.progressBar)
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(270, 350, 321, 41))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.ThreadCheckBox = QtWidgets.QCheckBox(self.splitter)
        self.ThreadCheckBox.setObjectName("ThreadCheckBox")
        self.ThreadCheckBox.toggled.connect(self.ThreadCheckBox_is_clild)
        self.widget1 = QtWidgets.QWidget(self.splitter)
        self.widget1.setObjectName("widget1")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.widget1)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_4 = QtWidgets.QLabel(self.widget1)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_5.addWidget(self.label_4)
        self.ThreadNumEntry = QtWidgets.QLineEdit(self.widget1)
        self.ThreadNumEntry.setObjectName("lineEdit")
        self.ThreadNumEntry.setEnabled(False)
        self.horizontalLayout_5.addWidget(self.ThreadNumEntry)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1018, 30))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.SearchKeyEntry, self.NovelnameradioButton)
        MainWindow.setTabOrder(self.NovelnameradioButton, self.WriterradioButton)
        MainWindow.setTabOrder(self.WriterradioButton, self.StartSearchButton)
        MainWindow.setTabOrder(self.StartSearchButton, self.DownloadNumEntry)
        MainWindow.setTabOrder(self.DownloadNumEntry, self.DownloadButton)
        MainWindow.setTabOrder(self.DownloadButton, self.Resulttable)
        MainWindow.setTabOrder(self.Resulttable, self.Infotext)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "笔趣阁小说下载器 3.0"))
        self.label_2.setText(_translate("MainWindow", "下载序号"))
        item = self.Resulttable.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "序号"))
        item = self.Resulttable.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "小说名"))
        item = self.Resulttable.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "作者"))
        item = self.Resulttable.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "链接"))
        self.StartSearchButton.setText(_translate("MainWindow", "搜  索"))
        self.DownloadButton.setText(_translate("MainWindow", "开 始 下 载"))
        self.label.setText(_translate("MainWindow", "搜索关键词"))
        self.NovelnameradioButton.setText(_translate("MainWindow", "按小说名搜索"))
        self.WriterradioButton.setText(_translate("MainWindow", "按作者名搜索"))
        self.label_6.setText(_translate("MainWindow", "保存地址"))
        self.label_3.setText(_translate("MainWindow", "下载进度"))
        self.ThreadCheckBox.setText(_translate("MainWindow", "多线程下载"))
        self.label_4.setText(_translate("MainWindow", "线程数"))

    def ThreadCheckBox_is_clild(self):
        if self.ThreadCheckBox.isChecked():
            Info = "多线程下载开启后，下载速度会加快，但开启过多线程会占用电脑资源及对网站造成一定的访问压力，因此本程序只允许开启至多60个线程。"
            messagebox = QMessageBox()
            messagebox.setWindowTitle("提示")
            messagebox.setText(Info)
            messagebox.addButton("我已知晓",QMessageBox.YesRole)
            messagebox.setWindowIcon(QtGui.QIcon("./resource/computer.ico"))
            messagebox.exec_()
            self.ThreadNumEntry.setText("60")
            self.ThreadNumEntry.setEnabled(True)
        else:
            self.ThreadNumEntry.clear()
            self.ThreadNumEntry.setEnabled(False)
    
    def Search(self):
        def start_search():
            self.StartSearchButton.setEnabled(False)
            self.Infotext.append("正在搜索。\n")
        def end_search():
            self.StartSearchButton.setEnabled(True)
        def getresult(status_code:int,ResultList:list):
            if status_code == 0:
                self.Infotext.append("该关键词无结果。\n")
            elif status_code == -1:
                self.Infotext.append("此次请求被网站拦截，请稍后再试！\n")
            else:
                row = 0
                cow = 0
                self.Resulttable.setRowCount(len(ResultList))
                for Result in ResultList:
                    for i in Result:
                        newitem = QtWidgets.QTableWidgetItem(i)
                        # 表格item居中
                        newitem.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                        newitem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                        self.Resulttable.setItem(row,cow,newitem)
                        cow += 1
                    row += 1
                    cow = 0
                self.Resulttable.resizeColumnsToContents()
                self.Resulttable.resizeRowsToContents()
                self.Resulttable.horizontalHeader().setStretchLastSection(True)
                self.Infotext.append("搜索完毕。\n")
                self.SearchKeyEntry.clear()
        flag = False
        self.Resulttable.clearContents()
        if self.SearchKeyEntry.text() == "":
            QMessageBox.about(None,"错误","请输入搜索关键词")
        else:
            if self.NovelnameradioButton.isChecked():
                searchtype = "articalname"
                flag = True
            elif self.WriterradioButton.isChecked():
                searchtype = "author"
                flag = True
            else:
                QMessageBox.about(None,"错误","请选择搜索模式")
            if flag == True:
                self.SearchThread = SearchThread(searchtype,self.SearchKeyEntry.text())
                self.SearchThread.signal.connect(getresult)
                self.SearchThread.started.connect(start_search)
                self.SearchThread.finished.connect(end_search)
                self.SearchThread.start()

    def Download(self):
        def start_download():
            self.DownloadButton.setEnabled(False)
            self.DownloadNumEntry.setEnabled(False)
            self.SavePlaceEntry.setEnabled(False)
            self.ThreadCheckBox.setEnabled(False)
            self.ThreadNumEntry.setEnabled(False)
            self.progressBar.reset()
            self.Infotext.append("\n开始下载。\n")
        def end_download():
            self.DownloadButton.setEnabled(True)
            self.DownloadNumEntry.setEnabled(True)
            self.SavePlaceEntry.setEnabled(True)
            self.ThreadCheckBox.setEnabled(True)
            self.ThreadNumEntry.setEnabled(True)
            self.Infotext.append("\n下载完成。\n")
        def set_progessbar(total):
            self.progressBar.setRange(0,total)
        def print_content(content):
            self.progressBar.setValue(self.progressBar.value()+1)
            self.Infotext.append(content)  
        def fin_info(result):
            if result == True:
                QMessageBox.about(None,"完成","下载完成！")
            else:
                QMessageBox.about(None,"错误","下载出错，请重新下载!")
        try:
            downloadnum = int(self.DownloadNumEntry.text())
            if self.Resulttable.rowCount() == 0:
                QMessageBox.about(None,"错误","该关键词无搜索结果。")
            else:
                if downloadnum > self.Resulttable.rowCount() or downloadnum < 1:
                    QMessageBox.about(None,"错误","输入序号有误，请重新输入。")
                else:
                    novelname = self.Resulttable.item(downloadnum-1,1).text()
                    novellink = self.Resulttable.item(downloadnum-1,3).text()
                    if self.ThreadCheckBox.isChecked():
                        try:
                            ThreadNum = int(self.ThreadNumEntry.text())
                            if ThreadNum > 60 or ThreadNum < 1:
                                QMessageBox.about(None,"错误","您未输入正确线程数，线程数将默认指定为60.")
                            ThreadNum = 60
                            self.ThreadNumEntry.setText("60")
                        except:
                            QMessageBox.about(None,"错误","您未输入线程数，线程数将默认指定为60.")
                            self.ThreadNumEntry.setText("60")
                            ThreadNum = 60
                    else:
                        ThreadNum = 1
                    saveplace = self.SavePlaceEntry.text()
                    if saveplace == "":
                        saveplace = "./Book/"
                    if os.path.exists(saveplace) == False:
                        QMessageBox.about(None,"提示","该目录不存在。")
                    else:
                        saveplace = saveplace + "/"
                        self.DownloadThread = DownloadThread(novelname,novellink,ThreadNum,saveplace)
                        self.DownloadThread.content_signal.connect(print_content)
                        self.DownloadThread.fin_signal.connect(fin_info)
                        self.DownloadThread.total_signal.connect(set_progessbar)
                        self.DownloadThread.started.connect(start_download)
                        self.DownloadThread.finished.connect(end_download)
                        self.DownloadThread.start()
        except:
            QMessageBox.about(None,"错误","请输入下载序号")
    
    def Run(self):
        app = QApplication(sys.argv)
        MainWin = QMainWindow()
        self.setupUi(MainWin)
        MainWin.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    Ui_MainWindow().Run()
