"""A spider for crawling Airbnb."""

import scrapy
import re
import json
import urllib
from datetime import datetime, timedelta
from scrapy.loader.processors import SelectJmes, MapCompose, TakeFirst
from scrapy.loader import ItemLoader
from zeus_research import items


class AirbnbSpider(scrapy.Spider):
    name = "airbnb_listings"
    last_offset = None
    current_page = 1
    current_count = 0

    def _next_pagination_url(self):
        url = 'https://www.airbnb.com/search/search_results?checkin={}&checkout={}&guests={}&source=bb&ss_id=29xicnfv&location={}&allow_override%5B%5D=&page={}'.format(
            urllib.quote_plus(self.checkin.strftime('%m/%d/%Y')),
            urllib.quote_plus(self.checkout.strftime('%m/%d/%Y')),
            self.guests,
            urllib.quote_plus(self.location),
            self.current_page)
        self.current_page += 1
        return url

    def __init__(self, checkin=None, checkout=None, location=None, guests=1, *args, **kwargs):
        super(AirbnbSpider, self).__init__(*args, **kwargs)
        if checkin:
            self.checkin = datetime.strptime(checkin.strip(), '%m-%d-%Y')
        else:
            self.checkin = datetime.utcnow() + timedelta(days=1)
        if checkout:
            self.checkout = datetime.strptime(checkout.strip(), '%m-%d-%Y')
        else:
            self.checkout = self.checkin + timedelta(days=30)
        if location:
            self.location = location
        else:
            location = 'San Francisco, CA'
        if guests:
            self.guests = int(guests)
        if self.checkout - self.checkin < timedelta(days=30):
            self.checkout = self.checkin + timedelta(days=30)


    def start_requests(self):
        urls = [
            self._next_pagination_url()
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        result = json.loads(response.text)
        next_offset = SelectJmes('results_json.metadata.pagination.next_offset')(result)
        if next_offset and next_offset != self.last_offset:
            self.log('Found next search offset: {}'.format(next_offset))
            self.last_offset = next_offset
            yield scrapy.Request(url=self._next_pagination_url())
        else:
            self.log('Reached the last offset of {}'.format(self.last_offset))

        country_code = SelectJmes('results_json.metadata.geography.country_code')(result)
        state_code = SelectJmes('results_json.metadata.geography.state_short')(result)
        search_results = SelectJmes('results_json.search_results')(result) or []
        for listing in search_results:
            zeus_listing = items.ZeusListingItem()
            zeus_listing['source'] = 'airbnb'
            zeus_listing['created_at'] = datetime.utcnow()
            zeus_listing['updated_at'] = datetime.utcnow()
            zeus_listing['scraper'] = self.name
            zeus_listing['source_rank'] = self.current_count
            self.current_count += 1
            zeus_listing['reviews_count'] = SelectJmes('listing.reviews_count')(listing)
            zeus_listing['average_rating'] = SelectJmes('listing.star_rating')(listing)
            zeus_listing['title'] = SelectJmes('listing.name')(listing)
            zeus_listing['bedrooms'] = SelectJmes('listing.bedrooms')(listing)
            zeus_listing['latitude'] = SelectJmes('listing.lat')(listing)
            zeus_listing['longitude'] = SelectJmes('listing.lng')(listing)
            zeus_listing['city'] = SelectJmes('listing.localized_city')(listing)
            zeus_listing['province'] = state_code
            zeus_listing['country'] = country_code
            zeus_listing['property_type'] = SelectJmes('listing.property_type')(listing)
            zeus_listing['monthly_rent'] = SelectJmes('pricing_quote.rate.amount')(listing)
            zeus_listing['post_last_seen_at'] = SelectJmes('listing.viewed_at')(listing)
            listing_id = SelectJmes('listing.id')(listing)
            if listing_id:
                zeus_listing['url'] = 'https://api.airbnb.com/v2/listings/{}?client_id=3092nxybyb0otqw18e8nh5nty&_format=v1_legacy_for_p3'.format(listing_id)
                request = scrapy.Request(url=zeus_listing['url'], callback=self.parse_listing)
                request.meta['item'] = zeus_listing
                self.log('Requesting listing url {}'.format(zeus_listing['url'].encode('utf-8')))
                yield request
            else:
                self.log('No id found for listing {}'.format(listing))
                yield zeus_listing

    def parse_listing(self, response):
        zeus_listing = response.meta['item']
        self.log('Parsing listing {}'.format(zeus_listing['title'].encode('utf-8')))
        result = json.loads(response.text)
        zeus_listing['bathrooms'] = SelectJmes('listing.bathrooms')(result)
        zeus_listing['neighborhood'] = SelectJmes('listing.neighborhood')(result)
        sqft = SelectJmes('listing.square_feet')(result)
        if sqft:
            zeus_listing['sqft'] = int(sqft)
        zeus_listing['province'] = SelectJmes('listing.state')(result) or zeus_listing['province']
        zeus_listing['country'] = SelectJmes('listing.country_code')(result) or zeus_listing['country']
        yield zeus_listing
