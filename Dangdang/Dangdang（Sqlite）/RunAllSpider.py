# from scrapy.crawler import CrawlerRunner
# from twisted.internet import reactor, defer
# from scrapy.utils.log import configure_logging
# from scrapy.utils.project import get_project_settings
# from Dangdang.spiders.changxiaobang import ChangxiaobangSpider
# from Dangdang.spiders.xinshuremaibang import XinshuremaibangSpider

# configure_logging()
# settings = get_project_settings()
# runner = CrawlerRunner(settings)

# @defer.inlineCallbacks
# def crawl():
#     yield runner.crawl(ChangxiaobangSpider)
#     yield runner.crawl(XinshuremaibangSpider)
#     reactor.stop()

# crawl()
# reactor.run()

from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from Dangdang.spiders.changxiaobang import ChangxiaobangSpider
from Dangdang.spiders.xinshuremaibang import XinshuremaibangSpider
from Dangdang.spiders.haopingbang import HaopingbangSpider

configure_logging()
settings = get_project_settings()
runner = CrawlerRunner(settings)
runner.crawl(ChangxiaobangSpider)
runner.crawl(XinshuremaibangSpider)
runner.crawl(HaopingbangSpider)
d = runner.join()
d.addBoth(lambda _: reactor.stop())

reactor.run()
