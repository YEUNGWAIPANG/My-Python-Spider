import datetime

def gettime():
    ctime=datetime.datetime.now()
    day=ctime.strftime("_%Y%m%d_")
    hms=ctime.strftime("%H%M%S")

    HMS=str(hms)
    hour=HMS[0:2]
    minute=HMS[2:4]
    second=HMS[4:6]
    nowtime=day+hour+"h"+minute+"m"+second+"s"
    return str(nowtime)
