from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, MapCompose, TakeFirst, Join
from w3lib.html import remove_tags

class Member(Item):
    """Member container for scraped data"""
    id = Field()
    party = Field()
    state = Field()
    phone = Field()
    last_name = Field()
    first_name = Field()
    district = Field()
    district_code = Field()
    body = Field()
