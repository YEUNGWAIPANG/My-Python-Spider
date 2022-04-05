import re
import scrapy
from lxml.html import etree
from Dangdang.items import DangdangXinshuremaibangItem

class XinshuremaibangSpider(scrapy.Spider):
    name = 'xinshuremaibang'
    
    def start_requests(self):
        for page in range(1,26):
            url = "http://bang.dangdang.com/books/newhotsales/01.00.00.00.00.00-24hours-0-0-1-" + str(page)
            yield scrapy.Request(url,callback=self.parse)

    def parse(self, response):
        item = DangdangXinshuremaibangItem()
        booklist = etree.HTML(response.text).xpath('//ul[@class="bang_list clearfix bang_list_mode"]/li')
        for book in booklist:
            bookname = book.xpath('./div[@class="name"]/a/@title')[0]
            writer = book.xpath('./div[@class="publisher_info"][1]/a[1]/text()')[0]
            press = book.xpath('./div[@class="publisher_info"][2]/a/text()')[0]
            nowprice = book.xpath('./div[@class="price"]/p/span[1]/text()')[0].replace("¥","")
            preprice = book.xpath('./div[@class="price"]/p/span[2]/text()')[0].replace("¥","")
            discount = book.xpath('./div[@class="price"]/p/span[3]/text()')[0].replace("折","")
            goodcomment_persent = re.findall(r'width: (.*?)%',book.xpath('./div[@class="star"]/span/span/@style')[0])[0]
            link = book.xpath('./div[@class="name"]/a/@href')[0]

            item['bookname'] = bookname
            item['writer'] = writer
            item['press'] = press
            item['nowprice'] = nowprice
            item['preprice'] = preprice
            item['discount'] = discount
            item['goodcomment_persent'] = goodcomment_persent
            item['link'] = link
            yield item
