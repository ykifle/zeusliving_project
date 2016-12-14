"""A spider for crawling Homesuite."""

import scrapy
import json
from datetime import datetime, timedelta
from scrapy.loader.processors import SelectJmes, MapCompose, TakeFirst, Compose
from scrapy.loader import ItemLoader
from zeus_research import items


class HomesuiteSpider(scrapy.Spider):
    name = "homesuite_listings"
    current_count = 0

    def __init__(self, checkin=None, checkout=None, *args, **kwargs):
        super(HomesuiteSpider, self).__init__(*args, **kwargs)
        if checkin:
            self.checkin = datetime.strptime(checkin.strip(), '%m-%d-%Y')
        else:
            self.checkin = datetime.utcnow() + timedelta(days=1)
        if checkout:
            self.checkout = datetime.strptime(checkout.strip(), '%m-%d-%Y')
        else:
            self.checkout = self.checkin + timedelta(days=30)
        if self.checkout - self.checkin < timedelta(days=30):
            self.checkout = self.checkin + timedelta(days=30)

    def start_requests(self):
        urls = [
            'https://www.yourhomesuite.com/listings?city=san%20francisco&center_lat=37.7749295&center_lng=-122.4194155&move_in_date={}&boundary_top_left_lat=37.818287608625354&boundary_top_left_lng=-122.47425374538483&boundary_bottom_right_lat=37.7315459486739&boundary_bottom_right_lng=-122.36451287722082&radius=2.9999859847017665&move_out_date={}'.format(
                self.checkin.strftime('%Y-%m-%d'),
                self.checkout.strftime('%Y-%m-%d'))
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        result = json.loads(response.text)
        next_page = SelectJmes('links.next')(result)
        if next_page:
            self.log('Found next page: {}'.format(next_page))
            yield scrapy.Request(url=next_page)
        listings = SelectJmes('listings')(result) or []
        for listing in listings:
            zeus_listing = items.ZeusListingItem()
            zeus_listing['source'] = 'homesuite'
            zeus_listing['created_at'] = datetime.utcnow()
            zeus_listing['updated_at'] = datetime.utcnow()
            zeus_listing['scraper'] = self.name
            zeus_listing['source_rank'] = self.current_count
            self.current_count += 1
            zeus_listing['title'] = SelectJmes('slug')(listing)
            zeus_listing['monthly_rent'] = SelectJmes('rent.monthly_rent')(listing)
            zeus_listing['bedrooms'] = SelectJmes('bedroom_count')(listing)
            zeus_listing['bathrooms'] = SelectJmes('bathroom_count')(listing)
            zeus_listing['latitude'] = SelectJmes('geography.lat')(listing)
            zeus_listing['longitude'] = SelectJmes('geography.lng')(listing)
            zeus_listing['city'] = SelectJmes('geography.city')(listing)
            zeus_listing['province'] = SelectJmes('geography.state_name')(listing)
            zeus_listing['country'] = SelectJmes('geography.country_name')(listing) or 'US'
            listing_url = SelectJmes('links.self')(listing)
            if listing_url:
                zeus_listing['url'] = listing_url
                request = scrapy.Request(url=zeus_listing['url'], callback=self.parse_listing)
                request.meta['item'] = zeus_listing
                self.log('Requesting listing url {}'.format(zeus_listing['url']))
                yield request
            else:
                self.log('No link found for listing {}'.format(listing['slug']))
                yield zeus_listing

    def parse_listing(self, response):
        zeus_listing = response.meta['item']
        self.log('Parsing listing {}'.format(zeus_listing['title']))
        il = ItemLoader(item=zeus_listing, response=response)
        il.default_output_processor = TakeFirst()
        il.add_css('post_updated_at', 'p.double-content.date span:contains("Last Updated")::text', MapCompose(lambda d: datetime.strptime(d.strip(), '%b %d, %Y')), re=':\s*(.*)')
        il.add_css('sqft', 'p:contains("Square Footage:") + span::text', MapCompose(lambda s: int(s) if s else None))
        il.add_css('property_type', 'p:contains("Housing Type:") + span::text')
        il.add_css('reviews_count', 'div#reviews_target > section.details-reviews > div.details-score::text', re='(\d+)')
        il.add_css('average_rating', 'div#reviews_target > section.details-reviews > div.details-score::text', Compose(lambda s: s[1] if len(s) > 1 else 0), re='(\d+)')
        yield il.load_item()
