import scrapy
import pymongo


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = pymongo.MongoClient()


    def _get_follow(self, response, selector_str, callback):
        for a_link in response.css(selector_str):
            url = a_link.attrib["href"]
            yield response.follow(url, callback=callback)

    def parse(self, response):
        yield from self._get_follow(
            response, ".TransportMainFilters_brandsList__2tIkv a.blackLink", self.brand_parse
        )

    def brand_parse(self, response):

        selectors = (
            ("div.Paginator_block__2XAPy a.Paginator_button__u1e7D", self.brand_parse),
            ("article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu", self.car_parse),
        )
        for selector, callback in selectors:
            yield from self._get_follow(response, selector, callback)

    def car_parse(self, response):
        data = {
            "title": response.css("div.AdvertCard_advertTitle__1S1Ak::text").extract_first(),
            "prise": response.css("div.AdvertCard_price__3dDCr::text").get().replace("\u2009", ""),
            "info": response.css("div.AdvertCard_descriptionInner__KnuRi::text").extract_first(),
            "specifications": {  #характеристики
                "year": response.css('.AdvertSpecs_row__ljPcX ::text').extract()[1],
                "mileage": response.css('.AdvertSpecs_row__ljPcX ::text').extract()[3],
                "bodyType": response.css('.AdvertSpecs_row__ljPcX ::text').extract()[5],
                "transmission": response.css('.AdvertSpecs_row__ljPcX ::text').extract()[7],
                "engineInfo": response.css('.AdvertSpecs_row__ljPcX ::text').extract()[9],
                "wheelType": response.css('.AdvertSpecs_row__ljPcX ::text').extract()[11],
                "color": response.css('.AdvertSpecs_row__ljPcX ::text').extract()[13],
                "driveType": response.css('.AdvertSpecs_row__ljPcX ::text').extract()[15],
                "enginePower": response.css('.AdvertSpecs_row__ljPcX ::text').extract()[17]},
            "equipment": response.css("div.AdvertEquipment_equipmentSection__3YpK5 "
                                      "div.AdvertEquipment_equipmentItem__Jk5c4::text").extract(),  # комплектация
               }
        print(data)
        self.db_client[self.crawler.settings.get("BOT_NAME","parser")][self.name].insert_one(data)

