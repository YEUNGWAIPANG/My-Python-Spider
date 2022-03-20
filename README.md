# My-Python-Spider
>[Biquge_downloader](/Biquge_downloader):笔趣阁小说下载，支持多线程下载，GUI界面由PyQt5实现。  
>>* [`Biquge_downloader.py`](/Biquge_downloader/Biquge_downloader.py):源码  
>>* `Biquge_downloader.exe`:源码通过Pyinstaller打包而成的exe可执行程序  
>>* [`resource`](/Biquge_downloader/resource/):资源文件  
>>>* `Bookshelf.ico`:程序图标  
>>>* `computer.ico`:消息框图标  
>>>* `fake_useragent_0.1.11.json`:fake_useragent库的请求头文件，如果没有的话调用"UserAgent().random"时可能会报错    

>[GetLessonTable](/GetLessonTable):从广东石油化工学院教务系统获取用户当周课表，GUI界面由PyQt5实现。
>>* [`GetLessonTable.py`](/GetLessonTable/GetLessonTable.py):源码  
>>* `computer.ico`：程序图标  
>>* `GetLessonTable.exe`:源码通过Pyinstaller打包而成的exe可执行程序     

>[Novelserver](./Novelserver)：定时检测用户在config.exe中配置的小说是否有更新，有更新就将最新章节发送到用户指定的邮箱，小说源为:[笔下文学](http://www.ywggzy.com/)，需要用户先在源码中填入发送最新章节的邮箱以及邮箱的授权码，接收邮箱可与发送邮箱一致。  
>>[`spider.py`](./Novelserver/spider.py):spider主体。  
>>[`config.py`](./Novelserver/config.py):配置程序源码。  
>>`config.exe`:配置程序的可执行程序，pyinstaller打包，界面由PyQt5实现。    
