import pymongo
import logging
from scrapy.exceptions import DropItem

logger = logging.getLogger(__name__)

class CheckDuplicatePipeline(object):

    collection_name = 'zeus_listings'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        existing_listing = self.db[self.collection_name].find_one({
            'latitude': item.get('latitude'),
            'longitude': item.get('longitude'),
            'neighborhood': item.get('neighborhood'),
            'city': item.get('city'),
            'province': item.get('province'),
            'country': item.get('country')
        })
        if existing_listing and not self._has_diffs(existing_listing, item):
            raise DropItem('Skipping duplicate listing {}'.format(item.get('title').encode('utf-8')))
        return item

    def _has_diffs(self, existing, item):
        comparable_fields = [ 'reviews_count',
                              'average_rating',
                              'source_rank',
                              'title',
                              'url',
                              'monthly_rent',
                              'bedrooms',
                              'bathrooms',
                              'sqft',
                              'property_type' ]
        for field in comparable_fields:
            if existing.get(field) != item.get(field):
                logger.info('Found difference in {}: {} != {}'.format(field,
                    existing.get(field),
                    item.get(field)))
                return True
        return False
