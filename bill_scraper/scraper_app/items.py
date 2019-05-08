from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, TakeFirst, MapCompose, TakeFirst, Join
from w3lib.html import remove_tags

class Bill(Item):
    """Bill container for scraped data"""
    id = Field(output_processor=Join())
    title = Field(output_processor=TakeFirst())
    latest_action_date = Field(output_processor=TakeFirst())
    latest_action = Field(output_processor=TakeFirst())
    latest_house_vote_date = Field(output_processor=TakeFirst())
    latest_house_vote_action = Field(output_processor=TakeFirst())
    latest_house_vote_roll = Field(output_processor=TakeFirst())
    latest_senate_vote_date = Field(output_processor=TakeFirst())
    latest_senate_vote_action = Field(output_processor=TakeFirst())
    latest_senate_vote_roll = Field(output_processor=TakeFirst())
    latest_cbo_date = Field(output_processor=TakeFirst())
    latest_cbo_url = Field(output_processor=TakeFirst())
    bill_number = Field(output_processor=Join())
    policy_area = Field()
    subjects = Field()
    bill_type = Field(output_processor=Join())
    origin_chamber = Field(output_processor=TakeFirst())
    cosponsor_ids = Field()
    sponsor_ids = Field()
    summary = Field(output_processor=TakeFirst())
    laws = Field(output_processor=Join())
    actions = Field(output_processor=Join())
    congress = Field(output_processor=Join())
    related_bills = Field(output_processor=Join())
    created_at = Field()
    latest_senate_vote_positions = Field()
    latest_house_vote_positions = Field()

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

class Law(Item):
    """Container for action items"""
    type = Field()
    number = Field()

class LawItemLoader(ItemLoader):
    default_input_processor = MapCompose(remove_tags)
    default_output_processor = TakeFirst()
    default_item_class = Law
