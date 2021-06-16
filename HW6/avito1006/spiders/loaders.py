from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from .css_selectors import FLAT



class AvitoLoader(ItemLoader):
    default_item_class = dict
    item_type_out = TakeFirst()
    url_out = TakeFirst()
    title_out = TakeFirst()
    price_out = TakeFirst()
    price_in = MapCompose(float)
    address_out = TakeFirst()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get("response"):
            self.add_value("url", self.context["response"].url)
        self.add_value("item_type", "real_estate")
        for key, selector in FLAT.items():
            self.add_css(key, **selector)



