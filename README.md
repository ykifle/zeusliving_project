# Zeusliving scraper

This project contains a web scraper that crawls a website and finds listing information for corporate renatls. Currently it supports the following websites.

  - www.airbnb.com
  - www.homesuite.com

Using the scraper you can export all listings available from Jan 01 2017 till Jan 31 2017 in San Francisco. You can export the data in a variaty of formats.

### Tech

This project uses a few opensource tools and APIs:

* [Scrapy] - Web scraper python library
* [Google Maps API] - Google's maps APIs
* [Redis] - An in-memory data structure store.

### Docker
The Zeus scrapers are easy run in a Docker container. First make sure you have Docker installed.

```sh
cd zeusliving_project
docker build . -t zeus_scraper
```
This will build the zeus_scraper image with everything needed to run the scrapers installed.

By default when you run this image it will run the command `scrapy crawl`. This command accepts the name of the scraper you want to run as an argument. Currently the options are:

  - airbnb_listings
  - homesuite_listings

So to run the scraper on airbnb listings:

```sh
docker run -v `pwd`:/zeusliving zeus_scraper airbnb_listings
```

You can use Google's Maps API to convert the scrapped longitudes and latitudes into address. To enable this pass in the `USE_GOOGLE_MAP_API` setting.

```sh
docker run -v `pwd`:/zeusliving zeus_scraper airbnb_listings -s USE_GOOGLE_MAP_API=1
```

Google as a daily limit on the requests you can make to the API. If you want to use Redis to cache the request responses for these API calls you can run a Redis docker container and link the zeus scraper container to that.

```sh
docker pull redis
docker run --name some-redis -d -v `pwd`/redis-data:/data redis
docker run -v `pwd`:/zeusliving --link some-redis:redis zeus_scraper homesuite_listings -s USE_GOOGLE_MAP_API=1
```

### Output

By default the scraper will just log each listing. To save it to a csv file you can pass the `-o` parameter.

```sh
docker run -v `pwd`:/zeusliving zeus_scraper airbnb_listings -o airbnb_listings.csv
```

Scrapy will create this file in the zeusliving/zeus_research directory.

### Todos

 - Write Tests

   [Scrapy]: <https://doc.scrapy.org/en/latest/index.html#>
   [Google Maps API]: <https://developers.google.com/maps/>
   [Redis]: <https://redis.io/>
