import multiprocessing
from Spiders.HushenAgu import HushenAguSpider
from Spiders.GanggutongSpider import GanggutongSpider
from Spiders.KechuangbanSpider import KechuangbanSpider

if __name__ == "__main__":
    spiderlist = [KechuangbanSpider(),GanggutongSpider(),HushenAguSpider()]
    cpu_total = multiprocessing.cpu_count()
    if cpu_total >= 3:
        pool = multiprocessing.Pool(3)
    else:
        pool = multiprocessing.Pool(1)
    
    for spider in spiderlist:
        pool.apply_async(spider.run) 
    pool.close()
    pool.join()
