"""A pipeline step that looks up listing address from lat and lng.

Can be enabled or disabled using USE_GOOGLE_MAP_API setting.
If you want to provide an API key use the GOOGLE_MAPS_API_KEY environment variable.
It will work without it though.
"""

import os
from scrapy.loader.processors import SelectJmes
from zeus_research import cache_client
from zeus_research import google_maps_client

class AddressLookupPipeline(object):
    def __init__(self, enabled):
        self.enabled = enabled

    def process_item(self, item, spider):
        if self.enabled and not item.get('address') and item.get('latitude') and item.get('longitude'):
            google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
            try:
                cache = cache_client.CacheClient()
            except cache_client.CacheClientConnectionError:
                cache = None
            maps_client = google_maps_client.GoogleMapsClient(api_key=google_maps_api_key, cache_client=cache)
            result = maps_client.reverse_geocode(item.get('latitude'), item.get('longitude'))
            status = SelectJmes('status')(result)
            address_results = SelectJmes('results')(result) or []
            if status == 'OK' and address_results:
                for address_result in result['results']:
                    address_types = SelectJmes('types')(address_result) or []
                    if 'street_address' in address_types:
                        item['address'] = SelectJmes('formatted_address')(address_result)
                        return item


        return item

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings.getbool('USE_GOOGLE_MAP_API'))