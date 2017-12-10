from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, TakeFirst, MapCompose, TakeFirst, Join
from w3lib.html import remove_tags

class Bill(Item):
    """Bill container for scraped data"""
    id = Field(output_processor=Join())
    title = Field(output_processor=TakeFirst())
    last_updated = Field(output_processor=TakeFirst())
    bill_number = Field(output_processor=Join())
    policy_area = Field()
    subjects = Field()
    bill_type = Field(output_processor=Join())
    cosponsor_ids = Field()
    sponsor_ids = Field()
    summary = Field(output_processor=TakeFirst())
    actions = Field(input_processor=Identity())
    congress = Field(output_processor=Join())
    related_bills = Field()

class BillAction(Item):
    """Container for action items"""
    date = Field()
    action = Field()

class ActionItemLoader(ItemLoader):
    default_input_processor = MapCompose(remove_tags)
    default_output_processor = TakeFirst()
    default_item_class = BillAction

class RelatedBill(Item):
    """Container for action items"""
    id = Field()
    title = Field()

class RelatedBillItemLoader(ItemLoader):
    default_input_processor = MapCompose(remove_tags)
    default_output_processor = TakeFirst()
    default_item_class = RelatedBill