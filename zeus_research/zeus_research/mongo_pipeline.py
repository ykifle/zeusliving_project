import pymongo
import logging
from datetime import datetime
from geojson import Point

logger = logging.getLogger(__name__)

class MongoPipeline(object):

    collection_name = 'zeus_listings'

    def __init__(self, mongo_uri, mongo_db, stats):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items'),
            stats=crawler.stats
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
        if existing_listing:
            logger.info('Inserting duplicate listing {}'.format(item.get('title').encode('utf-8')))
            item['dupe_of_id'] = existing_listing['_id']
            if self._post_updated(existing_listing, item):
                item['post_updated_at'] = datetime.utcnow()
                self.stats.inc_value('listings_updated')
        else:
            item['post_created_at'] = datetime.utcnow()
            self.stats.inc_value('new_listings_found')
        doc = dict(item)
        doc['location'] = Point((item.get('latitude'), item.get('longitude')))
        self.db[self.collection_name].insert(doc)
        self.stats.inc_value('listings_written_to_mongo')
        return item

    def _post_updated(self, existing, item):
        comparable_fields = [ 'title',
                              'monthly_rent',
                              'bedrooms',
                              'bathrooms',
                              'sqft',
                              'property_type' ]
        for field in comparable_fields:
            if existing.get(field) != item.get(field):
                logger.info('Post updated with difference in {}: {} != {}'.format(field,
                    existing.get(field),
                    item.get(field)))
                return True
        return False

