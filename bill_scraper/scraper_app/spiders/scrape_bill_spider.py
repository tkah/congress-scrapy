"""
Pylint requries too many docstrings. Finish this one later.
"""
import json
from datetime import datetime
from scrapy.spiders import XMLFeedSpider, CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Selector
from scrapy.http import Request
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Join, MapCompose
import urllib.request
from w3lib.html import remove_tags
from scraper_app.items import Bill, ActionItemLoader, LawItemLoader, RelatedBillItemLoader

from ..settings import CONGRESS, PROPUBLICA_KEY

class BillSpider(XMLFeedSpider):
    """
    Class to retrieve and parse HTML and XML
    from congress.gov bulk data
    """
    name = "congressionalbills"
    start_urls = [
        "https://www.govinfo.gov/bulkdata/xml/BILLSTATUS/" + CONGRESS
    ]
    itertag = "file"

    item_fields = {
        'title': './title/text()',
        'latest_action_date': './latestAction/actionDate/text()',
        'latest_action': './latestAction/text/text()',
        'bill_number': './billNumber/text()',
        'policy_area': './policyArea/name/text()',
        'subjects': './subjects/billSubjects/legislativeSubjects/item/name/text()',
        'bill_type': './billType/text()',
        'origin_chamber': './originChamber/text()',
        'sponsor_ids': './sponsors/item/bioguideId/text()',
        'cosponsor_ids': './cosponsors/item/bioguideId/text()',
        'summary': './summaries/billSummaries/item/text/text()'
    }

    # rules = (
    #     Rule(LinkExtractor(allow=r'BILLSTATUS')),
    #     Rule(LinkExtractor(allow=r'/BILLSTATUS-\w+\.xml$'), callback='parse_bills', follow=True)
    # )

    def parse_node(self, response, node):
        link = node.xpath('link/text()').get()
        yield Request(link, callback=self.parse_type_link)

    def parse_type_link(self, response):
        for bill in Selector(response).xpath('//files/file'):
            link = bill.xpath('link/text()').get()
            if "xml" not in link:
                continue
            yield Request(link, callback=self.parse_bills)

    def parse_bills(self, response):
        """ Required function for scrapy to parse URLs. """
        selector = Selector(response)

        headers = { "X-API-Key": PROPUBLICA_KEY }
        session = "1" if datetime.now().year % 2 == 1 else "2"
        roll_votes_first = "https://api.propublica.org/congress/v1/" + CONGRESS + "/"
        roll_votes_second = "/sessions/" + session + "/votes/" #17.json"

        bill = selector.xpath('//billStatus/bill')
        # Avoid adding to DB when /bill/updateDate is yesterday or earlier
        loader = ItemLoader(Bill(), selector=bill)
        loader.default_input_processor = MapCompose(remove_tags, str.strip)
        # loader.default_output_processor = Join()
        # iterate over fields and add xpaths to the loader
        for field, xpath in self.item_fields.items():
            loader.add_xpath(field, xpath)

        latest_cbo_date = None
        latest_cbo_url = None
        cbo_costs = bill.xpath('./cboCostEstimates')
        for item in cbo_costs.xpath('./item'):
            current_latest = None
            if (latest_cbo_date is not None):
                current_latest = datetime.strptime(latest_cbo_date, "%Y-%m-%dT%H:%M:%SZ")

            new_time = datetime.strptime(item.xpath('./pubDate/text()').extract_first(), "%Y-%m-%dT%H:%M:%SZ")
            if ((current_latest is not None and current_latest < new_time) or current_latest is None):
                latest_cbo_date = item.xpath('./pubDate/text()').extract_first()
                latest_cbo_url = item.xpath('./url/text()').extract_first()

        loader.add_value('latest_cbo_url', latest_cbo_url)
        loader.add_value('latest_cbo_date', latest_cbo_date)

        latest_house_vote_action = None
        latest_house_vote_roll = None
        latest_house_vote_date = None
        latest_senate_vote_action = None
        latest_senate_vote_roll = None
        latest_senate_vote_date = None
        recorded_votes = bill.xpath('./recordedVotes')
        for vote in recorded_votes.xpath('./recordedVote'):
            current_house_latest = None
            current_senate_latest = None

            if (latest_house_vote_date is not None):
                current_house_latest = datetime.strptime(latest_house_vote_date, "%Y-%m-%dT%H:%M:%SZ")

            if (latest_senate_vote_date is not None):
                current_senate_latest = datetime.strptime(latest_senate_vote_date, "%Y-%m-%dT%H:%M:%SZ")

            new_time = datetime.strptime(vote.xpath('./date/text()').extract_first(), "%Y-%m-%dT%H:%M:%SZ")
            new_chamber = vote.xpath('./chamber/text()').extract_first()
            if (new_chamber == 'Senate' and
                ((current_senate_latest is not None and current_senate_latest < new_time) or current_senate_latest is None)):
                latest_senate_vote_date = vote.xpath('./date/text()').extract_first()
                latest_senate_vote_roll = vote.xpath('./rollNumber/text()').extract_first()
                latest_senate_vote_action = vote.xpath('./fullActionName/text()').extract_first()
            elif (new_chamber == 'House' and
                ((current_house_latest is not None and current_house_latest < new_time) or current_house_latest is None)):
                latest_house_vote_date = vote.xpath('./date/text()').extract_first()
                latest_house_vote_roll = vote.xpath('./rollNumber/text()').extract_first()
                latest_house_vote_action = vote.xpath('./fullActionName/text()').extract_first()

        loader.add_value('latest_house_vote_action', latest_house_vote_action)
        loader.add_value('latest_house_vote_roll', latest_house_vote_roll)
        loader.add_value('latest_house_vote_date', latest_house_vote_date)
        loader.add_value('latest_senate_vote_action', latest_senate_vote_action)
        loader.add_value('latest_senate_vote_roll', latest_senate_vote_roll)
        loader.add_value('latest_senate_vote_date', latest_senate_vote_date)

        if (latest_house_vote_roll is not None):
            votes_obj = {}
            votes_url = roll_votes_first + "house" + roll_votes_second + latest_house_vote_roll + ".json"
            jsonresponse = urllib.request.urlopen(urllib.request.Request(votes_url, None, headers))
            response_data = json.loads(jsonresponse.read().decode())
            positions = response_data["results"]["votes"]["vote"]["positions"]
            for position in positions:
                votes_obj[position["member_id"]] = position["vote_position"]
            loader.add_value('latest_house_vote_positions', json.dumps(votes_obj))

        if (latest_senate_vote_roll is not None):
            votes_obj = {}
            votes_url = roll_votes_first + "senate" + roll_votes_second + latest_senate_vote_roll + ".json"
            jsonresponse = urllib.request.urlopen(urllib.request.Request(votes_url, None, headers))
            response_data = json.loads(jsonresponse.read().decode())
            positions = response_data["results"]["votes"]["vote"]["positions"]
            for position in positions:
                votes_obj[position["member_id"]] = position["vote_position"]
            loader.add_value('latest_senate_vote_positions', json.dumps(votes_obj))

        actions_arr = []
        for action in bill.xpath('./actions/item'):
            actions_arr.append(self.parse_actions(action))

        loader.add_value('actions', json.dumps(actions_arr))

        laws_arr = []
        for law in bill.xpath('./laws/item'):
            laws_arr.append(self.parse_laws(law))

        loader.add_value('laws', json.dumps(laws_arr))

        related_bills_arr = []
        for r_bill in bill.xpath('./relatedBills/item'):
            related_bills_arr.append(self.parse_related_bills(r_bill))

        loader.add_value('related_bills', json.dumps(related_bills_arr))

        loader.add_value('congress', CONGRESS)
        loader.add_value('id', response.url.split("/")[-1][11:-4])
        yield loader.load_item()

    def parse_bill_votes(self, response):
        response = urlopen(Request(req_url, None, headers))
        jsonresponse = json.loads(response.body_as_unicode())

    def parse_laws(self, response):
        action_loader = LawItemLoader(selector = response)
        action_loader.add_xpath('type', './type/text()')
        action_loader.add_xpath('number', './number/text()')
        return dict(action_loader.load_item())

    def parse_actions(self, response):
        action_loader = ActionItemLoader(selector = response)
        action_loader.add_xpath('date', './actionDate/text()')
        action_loader.add_xpath('action', './text/text()')
        return dict(action_loader.load_item())

    def parse_related_bills(self, response):
        related_loader = RelatedBillItemLoader(selector = response)
        related_loader.add_xpath('id', 'concat(./congress/text(), "", ./type/text(), "", ./number/text())')
        related_loader.add_xpath('title', './latestTitle/text()')
        return dict(related_loader.load_item())
