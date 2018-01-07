"""
Pylint requries too many docstrings. Finish this one later.
"""
import json
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import XmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from scrapy.loader.processors import Join, MapCompose
from w3lib.html import remove_tags
from scraper_app.items import Bill, ActionItemLoader, RelatedBillItemLoader

from ..settings import CONGRESS

class BillSpider(CrawlSpider):
    """
    Class to retrieve and parse HTML and XML
    from congress.gov bulk data
    """
    name = "congressionalbills"
    start_urls = [
        "https://www.gpo.gov/fdsys/bulkdata/BILLSTATUS/" + CONGRESS
    ]

    item_fields = {
        'title': './/bill/title/text()',
        'last_updated': './/bill/updateDate/text()',
        'bill_number': './/bill/billNumber/text()',
        'policy_area': './/bill/policyArea/name/text()',
        'subjects': './/bill/subjects/billSubjects/legislativeSubjects/item/name/text()',
        'bill_type': './/bill/billType/text()',
        'sponsor_ids': './/bill/sponsors/item/bioguideId/text()',
        'cosponsor_ids': './/bill/cosponsors/item/bioguideId/text()',
        'summary': './/bill/summaries/billSummaries/item/text/text()'
    }

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//div[@id="bulkdata"]', deny=(r'/BILLSTATUS$', r'/BILLSTATUS-\w+\.xml$'))),
        Rule(LinkExtractor(allow=r'/BILLSTATUS-\w+\.xml$'), callback='parse_bills', follow=True)
    )

    def parse_bills(self, response):
        """ Required function for scrapy to parse URLs. """
        selector = XmlXPathSelector(response)

        for bill in selector.select('//billStatus'):
            # Avoid adding to DB when /bill/updateDate is yesterday or earlier
            loader = XPathItemLoader(Bill(), selector=bill)
            loader.default_input_processor = MapCompose(remove_tags, str.strip)
            # loader.default_output_processor = Join()
            # iterate over fields and add xpaths to the loader
            for field, xpath in self.item_fields.items():
                loader.add_xpath(field, xpath)

            actions_arr = []
            for action in selector.select('//billStatus/bill/actions/item'):
                actions_arr.append(self.parse_actions(action))

            loader.add_value('actions', json.dumps(actions_arr))

            related_bills_arr = []
            for bill in selector.select('//billStatus/bill/relatedBills/item'):
                related_bills_arr.append(self.parse_related_bills(bill))

            loader.add_value('related_bills', json.dumps(related_bills_arr))

            loader.add_value('congress', CONGRESS)
            loader.add_value('id', response.url.split("/")[-1][11:-4])
            yield loader.load_item()

    def parse_actions(self, response):
        action_loader = ActionItemLoader(selector = response)
        action_loader.add_xpath('date', './/actionDate/text()')
        action_loader.add_xpath('action', './/text/text()')
        return dict(action_loader.load_item())

    def parse_related_bills(self, response):
        related_loader = RelatedBillItemLoader(selector = response)
        related_loader.add_xpath('id', 'concat(.//congress/text(), "", .//type/text(), "", .//number/text())')
        related_loader.add_xpath('title', './/latestTitle/text()')
        return dict(related_loader.load_item())
