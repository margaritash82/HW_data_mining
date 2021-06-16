from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess
from avito1006.spiders.avito import AvitoSpider


if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule("avito1006.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(AvitoSpider)
    crawler_process.start()