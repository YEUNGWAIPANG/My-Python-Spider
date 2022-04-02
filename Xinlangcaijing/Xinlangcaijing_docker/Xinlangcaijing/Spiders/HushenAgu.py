import pymysql
import requests
from time import sleep
from random import randint
from resources.Setting import *
from resources.Pretty import Pretty

class HushenAguSpider:
    def __init__(self) -> None:
        self.bankuai = "沪深A股"
        self.tablename = self.bankuai + nowtime
        self.link = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData"
        
    def getdata(self) -> list:
        datalist = []
        params = Pretty().Pretty_headers("""
            page: 1
            num: 80
            sort: symbol
            asc: 1
            node: hs_a
            symbol: 
            _s_r_a: inits
        """)
        params["page"] = int(params["page"])
        while True:
            print(self.bankuai + str(params["page"]))
            r = requests.get(self.link,params=params)
            r.raise_for_status()
            if len(r.json()) == 0:
                break
            else:
                for data in r.json():
                    result = []
                    result.append(data["symbol"])
                    result.append(data["name"])
                    result.append(data["trade"])
                    result.append(data["pricechange"])
                    result.append(data["changepercent"])
                    result.append(data["buy"])
                    result.append(data["sell"])
                    result.append(data["settlement"])
                    result.append(data["open"])
                    result.append(data["high"])
                    result.append(data["low"])
                    try:
                        float(str(data["volume"])[:-4] + "." + str(data["volume"])[-4:-2])
                        result.append(str(data["volume"])[:-4] + "." + str(data["volume"])[-4:-2])
                    except:
                        continue
                    try:
                        float(str(data["amount"])[:-4] + "." + str(data["amount"])[-4:-2])
                        result.append(str(data["amount"])[:-4] + "." + str(data["amount"])[-4:-2])
                    except:
                        continue
                    datalist.append(tuple(result))
                params["page"] += 1
                sleep(randint(2,5))
        return datalist

    def parse(self,datalist:list):
        try:
            db = pymysql.connect(host=MySQL_host,port=MySQL_port,user=MySQL_user,password=MySQL_password,database=MySQL_database)
        except pymysql.err.OperationalError:
            db = pymysql.connect(host=MySQL_host,port=MySQL_port,user=MySQL_user,password=MySQL_password)
            db.cursor().execute("CREATE DATABASE %s"%MySQL_database)
            db.commit()
            db.close()
            db = pymysql.connect(host=MySQL_host,port=MySQL_port,user=MySQL_user,password=MySQL_password,database=MySQL_database)
        db.cursor().execute("""
            CREATE TABLE %s(
                代码 TEXT NOT NULL,
                名称 TEXT NOT NULL,
                最新价	FLOAT NOT NULL,
                涨跌额	FLOAT NOT NULL, 
                涨跌幅	FLOAT NOT NULL,
                买入	FLOAT NOT NULL,
                卖出	FLOAT NOT NULL,
                昨收	FLOAT NOT NULL,
                今开	FLOAT NOT NULL,
                最高	FLOAT NOT NULL,
                最低	FLOAT NOT NULL,
                成交量（手） FLOAT NOT NULL,
                成交额（万） FLOAT NOT NULL
            )
        """%self.tablename)
        db.commit()
        db.cursor().executemany("INSERT INTO "+ self.tablename +" VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",datalist)
        db.commit()
        db.close()

    def run(self):
        self.parse(self.getdata())