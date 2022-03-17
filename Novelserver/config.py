import os
import sys
import ctypes
import sqlite3
import requests
from lxml import etree
from fake_useragent import UserAgent
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox

class GetbooknameThread(QtCore.QThread):
    signal = QtCore.pyqtSignal(str,str)
    resultsignal = QtCore.pyqtSignal(bool)

    def __init__(self,link):
        super(GetbooknameThread,self).__init__()
        self.link = link

    def run(self):
        try:
            r = requests.get(self.link,headers={"User-Agent":UserAgent(path='./fake_useragent_0.1.11.json').random})
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            r = etree.HTML(r.text)
            bookname = r.xpath('//div[@class="info"]/div/h1/text()')[0]
            result = True
        except:
            bookname = ""
            self.link = ""
            result = False
        self.signal.emit(bookname,self.link)
        self.resultsignal.emit(result)

class Config_Window(object):
    def __init__(self) -> None:
        self.need_delete_item = (None,None)
        self.GetbooknameThread = None
        if not os.path.exists("./book"):
            os.mkdir("./book")
        # 检查本地有没有数据库文件，没有就创建，有数据库文件但没有表就创建表
        if not os.path.exists("./taskdata.db"):
            self.db = sqlite3.connect("taskdata.db")
            self.db.cursor().execute("""
            CREATE TABLE linkstable(
                bookname TEXT NOT NULL UNIQUE,  
                link TEXT NOT NULL UNIQUE
            )
            """)
            self.db.commit()
        else:
            self.db = sqlite3.connect("./taskdata.db")
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

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 695)
        MainWindow.setFixedSize(800,695)
        MainWindow.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
        MainWindow.setWindowIcon(QtGui.QIcon("./chilun.ico"))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.linktable = QtWidgets.QTableWidget(self.centralwidget)
        self.linktable.setGeometry(QtCore.QRect(60, 160, 681, 381))
        self.linktable.setObjectName("linktable")
        self.linktable.setColumnCount(2)
        self.linktable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.linktable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.linktable.setHorizontalHeaderItem(1, item)
        self.linktable.horizontalHeader().setStretchLastSection(True)
        self.linktable.verticalHeader().setStretchLastSection(False)
        self.linktable.cellClicked.connect(self.get_need_delete_item)
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(62, 17, 681, 81))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.addButton = QtWidgets.QPushButton(self.layoutWidget)
        self.addButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.addButton.setObjectName("addButton")
        self.addButton.clicked.connect(self.pushlink)
        self.horizontalLayout.addWidget(self.addButton)
        self.deleteButton = QtWidgets.QPushButton(self.layoutWidget)
        self.deleteButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.deleteButton.setObjectName("deleteButton")
        self.deleteButton.clicked.connect(self.delelink)
        self.horizontalLayout.addWidget(self.deleteButton)
        self.saveButton = QtWidgets.QPushButton(self.layoutWidget)
        self.saveButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.saveButton.setObjectName("saveButton")
        self.saveButton.clicked.connect(self.save)
        self.horizontalLayout.addWidget(self.saveButton)
        self.refreshButton = QtWidgets.QPushButton(self.layoutWidget)
        self.refreshButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.refreshButton.setObjectName("reflashButton")
        self.horizontalLayout.addWidget(self.refreshButton)
        self.refreshButton.clicked.connect(self.refresh)
        self.layoutWidget1 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget1.setGeometry(QtCore.QRect(60, 90, 681, 71))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.layoutWidget1)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.LinkEntry = QtWidgets.QLineEdit(self.layoutWidget1)
        self.LinkEntry.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.LinkEntry.setObjectName("LinkEntry")
        self.horizontalLayout_2.addWidget(self.LinkEntry)
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(60, 570, 681, 61))
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName("textEdit")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 30))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.LinkEntry, self.addButton)
        MainWindow.setTabOrder(self.addButton, self.saveButton)
        MainWindow.setTabOrder(self.saveButton, self.refreshButton)
        MainWindow.setTabOrder(self.refreshButton, self.deleteButton)
        MainWindow.setTabOrder(self.deleteButton, self.linktable)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "接收更新任务配置器"))
        item = self.linktable.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "小说名"))
        item = self.linktable.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "小说首页链接"))
        self.addButton.setText(_translate("MainWindow", "添   加"))
        self.deleteButton.setText(_translate("MainWindow", "删   除"))
        self.saveButton.setText(_translate("MainWindow", "保   存"))
        self.refreshButton.setText(_translate("MainWindow", "刷  新"))
        self.label.setText(_translate("MainWindow", "链   接"))

    def pushlink(self):
        def Insert_to_table(bookname,booklink):
            if booklink != "" and booklink != "":
                self.linktable.setRowCount(self.linktable.rowCount() + 1)
                newitem = QtWidgets.QTableWidgetItem(bookname)
                newitem.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                newitem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.linktable.setItem(self.linktable.rowCount()-1,0,newitem)
                newitem = QtWidgets.QTableWidgetItem(booklink)
                newitem.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                newitem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.linktable.setItem(self.linktable.rowCount()-1,1,newitem)
                self.db.cursor().execute("INSERT INTO linkstable VALUES('%s','%s')"%(bookname,booklink))
                self.db.cursor().execute("""
                    CREATE TABLE '%s'(
                        sectionID INT UNIQUE NOT NULL,
                        sectionLink TEXT UNIQUE NOT NULL,
                        statuscode INT CHECK(statuscode = 0 OR statuscode = 1) NOT NULL
                    )
                """%bookname)
        def start_get():
            self.textEdit.clear()
            self.textEdit.append("\n正在获取电子书信息并添加。\n")
            self.addButton.setEnabled(False)
        def end_get(result):
            self.textEdit.clear()
            self.addButton.setEnabled(True)
            self.GetbooknameThread = None
            if result == True:
                self.textEdit.append("\n添加完毕。\n")
            else:
                self.textEdit.append("\n您输入的网址有误或服务器拒绝了访问,请稍后重试.\n")
        link = self.LinkEntry.text().strip()
        if link != "":
            exist_link = []
            for row in range(0,self.linktable.rowCount()):
                exist_link.append(self.linktable.item(row,1).text())
            if link not in exist_link:
                self.GetbooknameThread = GetbooknameThread(link)
                self.GetbooknameThread.signal.connect(Insert_to_table)
                self.GetbooknameThread.started.connect(start_get)
                self.GetbooknameThread.resultsignal.connect(end_get)
                self.GetbooknameThread.start()
            else:
                QMessageBox.about(None,"错误","链接已存在！")
        else:
            QMessageBox.about(None,"错误","未输入链接！")
        self.LinkEntry.clear()
    
    def get_need_delete_item(self,row,cow):
        self.need_delete_item = (row,cow)

    def delelink(self):
        if self.need_delete_item == (None,None):
            QMessageBox.about(None,"错误","没有选中链接！")
        else:
            bookname = self.linktable.item(self.need_delete_item[0],0).text()
            link = self.linktable.item(self.need_delete_item[0],self.need_delete_item[1]).text()
            # 选中了书名bookname列
            if self.need_delete_item[1] == 0:
                self.db.cursor().execute("DELETE FROM linkstable WHERE bookname = '%s'"%(bookname))
                self.linktable.removeRow(self.need_delete_item[0])
            # 选中了书链接link列
            else:
                self.db.cursor().execute("DELETE FROM linkstable WHERE link = '%s'"%(link))
                self.linktable.removeRow(self.need_delete_item[0])
            # 删除表
            self.db.cursor().execute("DROP TABLE '%s'"%bookname)
            self.need_delete_item = (None,None)

    def save(self):
        self.saveButton.setEnabled(False)
        self.db.commit()
        self.textEdit.clear()
        self.textEdit.append("\n配置保存完毕！\n")
        self.saveButton.setEnabled(True)

    def refresh(self):
        taskdata = []
        for data in self.db.cursor().execute("SELECT * FROM linkstable").fetchall():
            taskdata.append(data)
        self.linktable.setRowCount(len(taskdata))
        row = 0
        for data in taskdata:
            bookname = data[0]
            booklink = data[1]
            newitem = QtWidgets.QTableWidgetItem(bookname)
            newitem.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            newitem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.linktable.setItem(row,0,newitem)
            newitem = QtWidgets.QTableWidgetItem(booklink)
            newitem.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            newitem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.linktable.setItem(row,1,newitem)
            row += 1

    def run(self):
        app = QApplication(sys.argv)
        mainwin = QMainWindow()
        self.setupUi(mainwin)
        mainwin.show()
        self.refresh()
        sys.exit(app.exec_())

if __name__ == "__main__":
    Config_Window().run()
