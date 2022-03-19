# -*- coding: utf-8 -*-
import re
import scrapy
from lxml import etree
from douban.items import DoubanMovieItem,DoubanMusicItem,DoubanbookItem

class DoubanSpider(scrapy.Spider):
    name = 'douban'
    allowed_domains = ['www.douban.com']
    
    def start_requests(self):
        for page in range(0,226,25):
            url = "https://movie.douban.com/top250?start=" + str(page) + "&filter="
            yield scrapy.Request(url,callback=self.parse_movie)
        for page in range(0,226,25):
            url = "https://music.douban.com/top250?start=" + str(page) + "&filter="
            yield scrapy.Request(url,callback=self.parse_music)
        for page in range(0,226,25):
            url = "https://book.douban.com/top250?start=" + str(page) + "&filter="
            yield scrapy.Request(url,callback=self.parse_book)

    def parse_movie(self, response):
        item = DoubanMovieItem()
        movie = etree.HTML(response.text)

        movie_names = movie.xpath('//div[@class="hd"]/a/span[1]/text()')

        movie_info = movie.xpath('//div[@class="bd"]/p/text()')
        for i in movie_info:
            movie_info[movie_info.index(i)] = i.replace(u'\xa0','')
        for i in movie_info:
            movie_info[movie_info.index(i)] = i.replace('\n','')
        for i in movie_info:
            movie_info[movie_info.index(i)] = movie_info[movie_info.index(i)].replace(' ','')
        while '' in movie_info:
            movie_info.remove('')
        movie_workers = []
        movie_time_and_places = []
        for i in range(0,len(movie_info),2):
            movie_workers.append(movie_info[i])
            movie_time_and_places.append(movie_info[i + 1])
        
        movie_times = []
        movie_countries = []
        movie_types = []

        for i in movie_time_and_places:
            movie_times.append(i.split('/')[0])
            movie_countries.append(i.split('/')[1])
            movie_types.append(i.split('/')[2])

        movie_ratings = movie.xpath('//span[@class="rating_num"]/text()')
        movie_comments = movie.xpath('//div[@class="star"]/span[last()]/text()')
        for i in movie_comments:
            movie_comments[movie_comments.index(i)] = i.replace("人评价","")
        movie_describes = movie.xpath('//span[@class="inq"]/text()')
        for name,worker,time,country,movie_type,rating,comment,describe in zip(movie_names,movie_workers,movie_times,movie_countries,movie_types,movie_ratings,movie_comments,movie_describes):
            item['name'] = name
            item['worker'] = worker
            time = re.findall(r'\d+',time)[0]
            item['time'] = time
            item['country'] = country
            item['movie_type'] = movie_type
            item["rating"] = rating
            item['comment'] = comment
            item['describe'] = describe
            yield item

    def parse_music(self, response):
        item = DoubanMusicItem()
        music = etree.HTML(response.text)
        names = music.xpath('//div[@class="pl2"]/a/text()')
        for name in names:
            names[names.index(name)] = name.replace("\n","").strip()
        while '' in names:
            names.remove('')
        
        singers = []
        times = []
        specials = []
        styles = []

        musicinfos = music.xpath('//div[@class="pl2"]/p/text()')
        for musicinfo in musicinfos:
            singers.append(musicinfo.split("/")[0].strip())
            times.append(musicinfo.split("/")[1].strip())
            specials.append(musicinfo.split("/")[2].strip())
            styles.append(musicinfo.split("/")[4].strip())
        
        ratings = music.xpath('//div[@class="star clearfix"]/span[2]/text()')
        comments = music.xpath('//div[@class="star clearfix"]/span[3]/text()')
        for comment in comments:
            comments[comments.index(comment)] = re.findall(r'\d+',comment)[0]

        for name,singer,time,special,style,rating,comment in zip(names,singers,times,specials,styles,ratings,comments):
            item['name'] = name
            item['singer'] = singer
            item['time'] = time
            item['special'] = special
            item['style'] = style
            item['rating'] = rating
            item['comment'] = comment
            yield item
        
    def parse_book(self, response):
        item = DoubanbookItem()
        book = etree.HTML(response.text)

        booknames = book.xpath('//div[@class="pl2"]/a/text()')
        for bookname in booknames:
            booknames[booknames.index(bookname)] = bookname.replace("\n","")
        for bookname in booknames:   
            booknames[booknames.index(bookname)] = booknames[booknames.index(bookname)].strip()
        while '' in booknames:
            booknames.remove('')
        
        bookinfos = book.xpath('//div[@class="pl2"]/../p/text()')
        writers = []
        translators = []
        presses = []
        times = []
        prices = []

        for bookinfo in bookinfos:
            info = bookinfo.split("/")
            if len(info) == 4:
                writers.append(info[0])
                translators.append("无")
                presses.append(info[1])
                times.append(info[2])
                prices.append(info[3])
            elif len(info) == 5:
                writers.append(info[0])
                translators.append(info[1])
                presses.append(info[2])
                times.append(info[3])
                prices.append(info[4])
        ratings = book.xpath('//div[@class="star clearfix"]/span[2]/text()')
        comments = book.xpath('//div[@class="star clearfix"]/span[3]/text()')
        for comment in comments:
            comments[comments.index(comment)] = re.findall(r'\d+',comment)[0]

        for bookname,writer,translator,press,rating,time,comment,price in zip(booknames,writers,translators,presses,ratings,times,comments,prices):
            item["bookname"] = bookname
            item["writer"] = writer
            item["translator"] = translator
            item["press"] = press
            item["rating"] = rating
            item["time"] = time
            item["comment"] = comment
            item["price"] = price.replace("元","")
            yield item
