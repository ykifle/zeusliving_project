"""A client for making requests to a Redis cache."""

import redis
import logging
from redis.exceptions import ConnectionError

_redis_client = None
logger = logging.getLogger(__name__)

class CacheClientConnectionError(Exception):
  pass

class CacheClient(object):
  def __init__(self, host='redis', port=6379):
    global _redis_client
    if not _redis_client:
      _redis_client = redis.StrictRedis(host=host, port=port, db=0)
      try:
        _redis_client.ping()
      except ConnectionError as e:
        _redis_client = None
        raise CacheClientConnectionError(e)
    self.client = _redis_client

  def get(self, key):
    return self.client.get(key)

  def set(self, key, value):
    return self.client.set(key, value)