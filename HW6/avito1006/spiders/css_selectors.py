ALL_FLAT = {
    "selector": "div.iva-item-titleStep-2bjuh a.iva-item-title-1Rmmj",
    "callback": "flat_data_parse"
}

FLAT = {
    "title": lambda resp: resp.css('.title-info-main ::text'),
    "price":  lambda resp: resp.css('span.js-item-price').attrs['content'],
    "address": lambda resp: resp.css('span.item-address__string::text'),

}
