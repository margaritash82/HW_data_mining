import scrapy
from .css_selectors import ALL_FLAT
from .loaders import AvitoLoader


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/krasnoyarsk/kvartiry/prodam']

    def parse(self, response):
        yield response.follow(
            response.xpath("//a[@data-category-id='24'][@title='Все квартиры']/@href").get(),
            callback=self.flat_parse,
        )


    def flat_parse(self, response):

        for url in response.css(ALL_FLAT["selector"]):
            url = response.css(ALL_FLAT["selector"]).attrib['href']
            yield response.follow(url, getattr(self, ALL_FLAT["callback"]))

        for el in range(1, 101):
            yield response.follow(f"?p={el}", callback=self.flat_parse)

    def flat_data_parse(self, response):
        loader = AvitoLoader(response=response)
        yield loader.load_item()

