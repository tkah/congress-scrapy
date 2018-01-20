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

from scraper_app.items import Member

class MemberSpider(CrawlSpider):
    """
    Class to retrieve and parse HTML and XML
    from house and senate member data
    """
    name = "congressionalmembers"
    start_urls = [
        "https://www.senate.gov/general/contact_information/senators_cfm.xml",
        "http://clerk.house.gov/xml/lists/MemberData.xml"
    ]

    house_fields = {
        'id': './member-info/bioguideID/text()',
        'party': './member-info/party/text()',
        'state': './member-info/state/@postal-code',
        'phone': './member-info/phone/text()',
        'last_name': './member-info/lastname/text()',
        'first_name': './member-info/firstname/text()',
        'district_code': './statedistrict/text()',
        'district': './member-info/district/text()'
    }

    senate_fields = {
        'id': './bioguide_id/text()',
        'party': './party/text()',
        'state': './state/text()',
        'phone': './phone/text()',
        'last_name': './last_name/text()',
        'first_name': './first_name/text()'
    }

    def parse(self, response):
        """ Required function for scrapy to parse URLs. """
        selector = XmlXPathSelector(response)

        if 'senate' in response.url:
            for member in selector.select('//contact_information/member'):
                # Avoid adding to DB when /bill/updateDate is yesterday or earlier
                loader = XPathItemLoader(Member(), selector=member)
                loader.default_input_processor = MapCompose(remove_tags, str.strip)
                loader.default_output_processor = Join()
                # iterate over fields and add xpaths to the loader
                for field, xpath in self.senate_fields.items():
                    loader.add_xpath(field, xpath)

                loader.add_value('body', 'senate')
                yield loader.load_item()

        if 'house' in response.url:
            for member in selector.select('//MemberData/members/member'):
                # Avoid adding to DB when /bill/updateDate is yesterday or earlier
                loader = XPathItemLoader(Member(), selector=member)
                loader.default_input_processor = MapCompose(remove_tags, str.strip)
                loader.default_output_processor = Join()
                # iterate over fields and add xpaths to the loader
                for field, xpath in self.house_fields.items():
                    loader.add_xpath(field, xpath)

                loader.add_value('body', 'house')
                yield loader.load_item()
