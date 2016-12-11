import scrapy


class ZeusListingItem(scrapy.Item):
    id = scrapy.Field() #
    batch_id = scrapy.Field() #
    source = scrapy.Field()
    neighborhood = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()
    post_created_at = scrapy.Field() #
    post_updated_at = scrapy.Field() #
    reviews_count = scrapy.Field()
    average_rating = scrapy.Field()
    source_rank = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    monthly_rent = scrapy.Field()
    bedrooms = scrapy.Field()
    bathrooms = scrapy.Field()
    sqft = scrapy.Field()
    address = scrapy.Field() #
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    dupe_of_id = scrapy.Field() #
    city = scrapy.Field()
    province = scrapy.Field()
    country = scrapy.Field()
    property_type = scrapy.Field()
    post_first_seen_at = scrapy.Field()
    post_last_seen_at = scrapy.Field()
    scraper = scrapy.Field()
