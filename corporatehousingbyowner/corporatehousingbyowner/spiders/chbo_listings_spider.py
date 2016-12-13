import scrapy
import re


class CHBOSpider(scrapy.Spider):
    name = "chbo_listings"

    def start_requests(self):
        url = 'https://www.corporatehousingbyowner.com'
        yield scrapy.Request(url=url, callback=self.after_session)

    def after_session(self, response):
        urls = [
            'https://www.corporatehousingbyowner.com/search/San-Francisco--CA--United-States/?arrival_date=12-09-2016&deprt_date=01-09-2017&page=1&slat=37.61439732133598&slng=-122.27453200000002&szoom=9',
            # 'https://www.corporatehousingbyowner.com/search/San-Francisco--CA--United-States/?arrival_date=12-09-2016&deprt_date=01-09-2017&page=2&slat=37.61439732133598&slng=-122.27453200000002&szoom=9',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for num in response.css('.search-top-pagination a::text').extract():
            yield scrapy.Request(url='https://www.corporatehousingbyowner.com/search/San-Francisco--CA--United-States/?arrival_date=12-09-2016&deprt_date=01-09-2017&page={}&slat=37.61439732133598&slng=-122.27453200000002&szoom=9'.format(num))
        for href in response.css('a.prop_view::attr(href)').extract():
            yield scrapy.Request(url=response.urljoin(href), callback=self.parse_listing)

    def parse_listing(self, response):
        def extract_with_css(query):
            return response.css(query).extract_first().strip()
        def extract_with_xpath(query):
            return response.xpath(query).extract_first().strip()

        yield {
            'city': extract_with_css('ul.features span:contains("City") + a::text'),
            'state': extract_with_css('ul.features span:contains("State") + a::text'),
            'country': extract_with_css('ul.features span:contains("Country") + a::text'),
            'zip': extract_with_xpath('//ul[@class="features"]//span[contains(text(), "Zip")]/parent::*/text()'),
            'cross_streets': extract_with_css('ul.features span:contains("Cross Streets") + p::text').split(',')
        }