# -*- coding: utf-8 -*-

# Scrapy settings for zeus_research project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'zeus_research'

SPIDER_MODULES = ['zeus_research.spiders']
NEWSPIDER_MODULE = 'zeus_research.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure item pipelines
ITEM_PIPELINES = {
    'zeus_research.check_duplicate_pipeline.CheckDuplicatePipeline': 300,
    'zeus_research.pipelines.AddressLookupPipeline': 400,
    'zeus_research.mongo_pipeline.MongoPipeline': 500,
}

# Enable and configure the AutoThrottle extension (disabled by default)
AUTOTHROTTLE_ENABLED = True

FEED_FORMAT = 'csv'
FEED_EXPORT_FIELDS = ['id', 'batch_id', 'source', 'neighborhood', 'created_at', 'updated_at', 'post_created_at', 'post_updated_at', 'reviews_count', 'average_rating', 'source_rank', 'title', 'url', 'monthly_rent', 'bedrooms', 'bathrooms', 'sqft', 'address', 'latitude', 'longitude', 'dupe_of_id', 'city', 'province', 'country', 'property_type', 'post_first_seen_at', 'post_last_seen_at', 'scraper']

USE_GOOGLE_MAP_API = False
MONGO_URI = 'mongodb://mongo:27017/'
MONGO_DATABASE = 'items'
USE_MONGO = False
