"""A client for making requests to Google maps API."""

import requests
import json
import logging

GEOCODE_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

logger = logging.getLogger(__name__)

class GoogleMapsClient(object):
  def __init__(self, api_key=None, cache_client=None):
    self.api_key = api_key
    self.cache_client = cache_client

  def reverse_geocode(self, lat, lng):
    """Looks up address from lat and lng and caches result."""
    result = None
    if self.cache_client:
      result = self.cache_client.get(self._geocode_key(lat, lng))
    if not result:
      params={'latlng': '{},{}'.format(lat, lng)}
      if self.api_key:
        params['key'] = self.api_key
      response = requests.get(GEOCODE_API_URL, params=params)
      if response.status_code != 200:
        return None
      result = response.content
      if self.cache_client:
        self.cache_client.set(self._geocode_key(lat, lng), result)
    else:
      logger.info('Found key {} in cache'.format(self._geocode_key(lat, lng)))
    return json.loads(result)

  def _geocode_key(self, lat, lng):
    """Create a cache key from lat and lng."""
    return '{}+{}'.format(lat, lng)