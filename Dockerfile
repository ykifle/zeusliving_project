FROM fedora:22
RUN dnf update -y && dnf install -y \
  gcc \
  libffi-devel \
  python-devel \
  openssl-devel \
  libxml2-devel \
  libxslt-devel

RUN pip install \
  jmespath \
  pymongo \
  geojson \
  redis \
  requests \
  Scrapy

WORKDIR /zeusliving/zeus_research
ENTRYPOINT ["scrapy", "crawl"]